ARG BASE_IMAGE=ds60sqlpy-worker-cpp20:1.3.0
FROM ${BASE_IMAGE}
USER root
WORKDIR /opt/native-ad
COPY prepare_sdk.py /opt/native-ad/prepare_sdk.py
RUN python3 prepare_sdk.py /opt/native-ad/vendor
COPY gaussian_checks.hpp tmbad_probe.cpp /opt/native-ad/
RUN g++ -std=c++17 -O1 -g0 -I/opt/native-ad/vendor/include -I/opt/native-ad/vendor/eigen -I/opt/native-ad \
    tmbad_probe.cpp -ldl -o native_probe \
    && ! command -v R >/dev/null 2>&1 \
    && ./native_probe \
    && ldd ./native_probe >runtime-libraries.txt \
    && ! grep -E 'libR[.]|libpython' runtime-libraries.txt
USER 65534:65534
ENTRYPOINT ["/opt/native-ad/native_probe"]
