# R 4.6.1 is compiled from the SHA-256 verified upstream source on the shared
# Debian 13 slim Python base used by the other workers. Debian 13 packages R
# 4.5, and the locked CRAN closure targets 4.6.1. Building here keeps the worker
# off Ubuntu, whose kernel headers carried open advisories, and keeps the
# worker's patched CPython at /usr/local/bin/python3. Stages: r-source builds
# cairo and R, r-runtime holds the runtime libraries and learner toolchain,
# r-packages compiles the locked CRAN closure with the extra library headers,
# and the final image copies only the compiled site library onto r-runtime.
ARG DS60_R_IMAGE=python:3.12.16-slim-trixie@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
FROM ${DS60_R_IMAGE} AS r-source
ARG R_VERSION=4.6.1
ARG R_SOURCE_SHA256=4da6e61d2c0aac5f14a2e7e432cb5fcc269efe83da4293050ba7f03dff4e2cf4
ARG CAIRO_VERSION=1.18.6
ARG CAIRO_SOURCE_SHA256=1c767308174337a74694da0f3ec069c271452163a1ef4540964c50c301f157d4
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl g++ gcc gfortran make perl pkgconf file zip unzip xz-utils meson ninja-build \
    libblas-dev liblapack-dev libbz2-dev libcurl4-openssl-dev libdeflate-dev libfontconfig-dev \
    libfreetype-dev libicu-dev libjpeg-dev liblzma-dev libpcre2-dev libpixman-1-dev libpng-dev \
    libreadline-dev libzstd-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*
# Debian's cairo links the X11 client libraries, which carry open advisories and
# have no use in a headless worker. This cairo is built from the SHA-256 verified
# upstream source with only the image, PDF, PostScript and SVG surfaces, FreeType
# and fontconfig text, and no X11, XCB or GLib.
WORKDIR /usr/src/cairo
RUN curl -fsSL --retry 5 --retry-all-errors -o /tmp/cairo.tar.xz \
       "https://cairographics.org/releases/cairo-${CAIRO_VERSION}.tar.xz" \
    && echo "${CAIRO_SOURCE_SHA256}  /tmp/cairo.tar.xz" | sha256sum -c - \
    && tar -xJf /tmp/cairo.tar.xz --strip-components=1 && rm /tmp/cairo.tar.xz \
    && meson setup build --prefix=/usr/local --libdir=lib --buildtype=release --wrap-mode=nodownload \
         -Dxlib=disabled -Dxcb=disabled -Dtee=disabled -Dglib=disabled -Dspectre=disabled \
         -Dlzo=disabled -Dsymbol-lookup=disabled -Dtests=disabled -Dgtk_doc=false \
         -Dpng=enabled -Dzlib=enabled -Dfreetype=enabled -Dfontconfig=enabled \
    && meson install -C build --strip && ldconfig \
    && pkgconf --exists cairo-png cairo-ft cairo-pdf cairo-svg && ! pkgconf --exists cairo-xlib
WORKDIR /usr/src/R
RUN curl -fsSL --retry 5 --retry-all-errors -o /tmp/R.tar.gz \
       "https://cloud.r-project.org/src/base/R-4/R-${R_VERSION}.tar.gz" \
    && echo "${R_SOURCE_SHA256}  /tmp/R.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/R.tar.gz --strip-components=1 && rm /tmp/R.tar.gz
# The configure options match the previous Ubuntu-based R build: shared libR,
# memory profiling, readline, system BLAS and LAPACK and the recommended
# packages. Graphics use the cairo above; there is no display, so X11 and Tcl/Tk
# are off, and the unused TIFF device is left out with its library.
RUN R_PAPERSIZE=letter R_BATCHSAVE="--no-save --no-restore" PERL=/usr/bin/perl \
       R_UNZIPCMD=/usr/bin/unzip R_ZIPCMD=/usr/bin/zip LIBnn=lib AWK=/usr/bin/awk \
       CFLAGS="-g -O2 -fstack-protector-strong -Wformat -Werror=format-security -Wdate-time -D_FORTIFY_SOURCE=2" \
       CXXFLAGS="-g -O2 -fstack-protector-strong -Wformat -Werror=format-security -Wdate-time -D_FORTIFY_SOURCE=2" \
       ./configure --prefix=/usr/local --enable-R-shlib --enable-memory-profiling --with-readline \
         --with-blas --with-lapack --with-recommended-packages --with-cairo --with-x=no --without-tcltk \
         --without-libtiff \
    && make -j"$(nproc)" && make install-strip \
    && /usr/local/bin/Rscript --vanilla -e 'stopifnot(getRversion() == "4.6.1", capabilities("cairo"), capabilities("profmem"))'

FROM ${DS60_R_IMAGE} AS r-runtime
# Runtime libraries for R, its cairo devices and the locked packages, OpenBLAS as
# the BLAS and LAPACK provider, and the en_US.UTF-8 locale. The C, C++ and
# Fortran compilers, make, pkg-config and the C library and BLAS headers stay
# installed: learners build and install local source packages (R CMD INSTALL,
# Rcpp, cpp11) into a per-job library, and the classroom qualification proves
# that path. The worker stays offline, so the network and XML headers that only
# the locked CRAN packages need live in the build stage below. Python packages
# are never installed, so pip is removed.
# hadolint ignore=DL3005,DL3008
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    ca-certificates locales tzdata zip unzip fontconfig fonts-dejavu-core \
    libbz2-1.0 libcurl4t64 libdeflate0 libfontconfig1 libfreetype6 libgomp1 libicu76 \
    libjpeg62-turbo liblzma5 libpcre2-8-0 libpixman-1-0 libpng16-16t64 libreadline8t64 \
    libssl3t64 libuv1t64 libxml2 libzstd1 zlib1g libopenblas0-pthread \
    g++ gcc gfortran make pkgconf libc6-dev libblas-dev liblapack-dev \
    && sed -i 's/^# *\(en_US.UTF-8 UTF-8\)/\1/' /etc/locale.gen && locale-gen \
    && python -m pip uninstall --yes pip \
    && rm -rf /var/lib/apt/lists/* && install -d -m 0700 /run/ds60
COPY --from=r-source /usr/local/lib/libcairo.so.2* /usr/local/lib/
COPY --from=r-source /usr/local/lib/R /usr/local/lib/R
COPY --from=r-source /usr/local/bin/R /usr/local/bin/Rscript /usr/local/bin/
ENV R_HOME=/usr/local/lib/R LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 TZ=Etc/UTC
RUN ldconfig && install -d -m 2775 -g staff /usr/local/lib/R/site-library \
    && echo "R_LIBS=\${R_LIBS-'/usr/local/lib/R/site-library:/usr/local/lib/R/library'}" \
       >> /usr/local/lib/R/etc/Renviron.site \
    && Rscript --vanilla -e 'stopifnot(getRversion() == "4.6.1", capabilities("cairo"), grepl("openblas", La_library()))'

FROM r-runtime AS r-packages
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcurl4-openssl-dev libssl-dev libxml2-dev libuv1-dev libicu-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*
COPY docker/workers/r/packages.lock.json /tmp/r-packages.lock.json
COPY docker/workers/r/install_packages.py /tmp/install_packages.py
# The openssl package's vignette embeds sample private keys that secret scans flag.
RUN python3 /tmp/install_packages.py \
    && rm -rf /usr/local/lib/R/site-library/openssl/doc

FROM r-runtime
COPY --from=r-packages /usr/local/share/ds60-build-logs /usr/local/share/ds60-build-logs
COPY --from=r-packages /usr/local/lib/R/site-library /usr/local/lib/R/site-library
# Without Pango, R makes Xlib the default bitmap type, and there is no display.
# Sessions that read the site profile (projects, R CMD INSTALL, interactive R)
# use cairo; the classroom runner sets the same option because it runs --vanilla.
RUN echo 'options(bitmapType = "cairo")' >> /usr/local/lib/R/etc/Rprofile.site \
    && Rscript -e 'stopifnot(identical(getOption("bitmapType"), "cairo")); grDevices::png(tempfile(fileext = ".png")); plot(1); invisible(grDevices::dev.off())' \
    && Rscript --vanilla -e 'invisible(lapply(rownames(installed.packages(lib.loc = .libPaths()[1])), loadNamespace))'
WORKDIR /opt/worker
COPY src/ds60sqlpy/__init__.py src/ds60sqlpy/http_server.py src/ds60sqlpy/module_worker.py src/ds60sqlpy/worker_operations.py src/ds60sqlpy/plot_artifacts.py src/ds60sqlpy/plot_capture.py src/ds60sqlpy/worker_figures.py src/ds60sqlpy/worker_figures.R /opt/worker/src/ds60sqlpy/
ENV PYTHONPATH=/opt/worker/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_WORKER_PROFILE=r-statistics
ENTRYPOINT ["python3", "-m", "ds60sqlpy.module_worker", "--host", "0.0.0.0", "--port", "8081"]
# Keep the revision last so a new commit reuses every earlier cached layer.
ARG DS60_SOURCE_REVISION=""
ARG DS60_RELEASE_VERSION=""
LABEL org.opencontainers.image.revision="${DS60_SOURCE_REVISION}" \
    org.opencontainers.image.version="${DS60_RELEASE_VERSION}" \
    org.opencontainers.image.source="https://github.com/sadatnfs/ds60sqlpy"
