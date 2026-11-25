#!/usr/bin/env python3
"""Prove that the R worker builds compiled source packages offline.

The probe runs as an ordinary classroom job, so it uses the real worker
limits: an unprivileged user, a read-only image, a private network and a
per-job temporary directory. It writes a small package with C, C++ (cpp11
headers) and Fortran sources, installs it with ``R CMD INSTALL`` into a
per-job library, calls each routine, and compiles one Rcpp function. The run
uses the worked-solution purpose so it never replaces a learner's draft.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Protocol

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.check_classroom_profiles import TERMINAL, ClassroomClient  # noqa: E402

LESSON_ID = "r-001"
PROFILE = "r-statistics"
MARKER = "r-toolchain checks passed: C, C++ (cpp11), Fortran and Rcpp"

# R raw strings keep the C, C++ and Fortran sources free of escapes.
PROBE_SOURCE = r"""
stopifnot(Sys.info()[["effective_user"]] != "root")
root <- file.path(tempdir(), "ds60-toolchain")
lib <- file.path(root, "library")
pkg <- file.path(root, "ds60toolchain")
dir.create(lib, recursive = TRUE)
dir.create(file.path(pkg, "R"), recursive = TRUE)
dir.create(file.path(pkg, "src"))
stopifnot(file.access(.Library, 2) != 0)

writeLines(c(
  "Package: ds60toolchain",
  "Version: 0.0.1",
  "Title: Classroom Compiler Qualification",
  "Description: Proves that C, C++ and Fortran sources build offline.",
  "Author: DS60 Classroom",
  "Maintainer: DS60 Classroom <classroom@example.invalid>",
  "License: GPL-3",
  "LinkingTo: cpp11"
), file.path(pkg, "DESCRIPTION"))
writeLines(c(
  "useDynLib(ds60toolchain, .registration = TRUE, .fixes = \"C_\")",
  "export(c_sum, cpp11_dot, f_scale)"
), file.path(pkg, "NAMESPACE"))
writeLines(r"(
c_sum <- function(x) .Call(C_c_sum, as.double(x))
cpp11_dot <- function(x, y) .Call(C_cpp11_dot, as.double(x), as.double(y))
f_scale <- function(x, factor) {
  .Fortran(C_fscale, n = length(x), x = as.double(x), factor = as.double(factor))$x
}
)", file.path(pkg, "R", "api.R"))
writeLines(r"(
#include <R.h>
#include <Rinternals.h>
#include <R_ext/Rdynload.h>

SEXP cpp11_dot(SEXP x, SEXP y);
void F77_NAME(fscale)(int *n, double *x, double *factor);

SEXP c_sum(SEXP x) {
  double total = 0.0;
  for (R_xlen_t i = 0; i < XLENGTH(x); i++) total += REAL(x)[i];
  return ScalarReal(total);
}

static const R_CallMethodDef call_methods[] = {
  {"c_sum", (DL_FUNC) &c_sum, 1},
  {"cpp11_dot", (DL_FUNC) &cpp11_dot, 2},
  {NULL, NULL, 0}
};

static const R_FortranMethodDef fortran_methods[] = {
  {"fscale", (DL_FUNC) &F77_NAME(fscale), 3},
  {NULL, NULL, 0}
};

void R_init_ds60toolchain(DllInfo *dll) {
  R_registerRoutines(dll, NULL, call_methods, fortran_methods, NULL);
  R_useDynamicSymbols(dll, FALSE);
}
)", file.path(pkg, "src", "init.c"))
writeLines(r"(
#include <numeric>
#include "cpp11/declarations.hpp"
#include "cpp11/doubles.hpp"

extern "C" SEXP cpp11_dot(SEXP x, SEXP y) {
  BEGIN_CPP11
  cpp11::doubles left(x);
  cpp11::doubles right(y);
  if (left.size() != right.size()) cpp11::stop("Vectors must have the same length.");
  return cpp11::as_sexp(std::inner_product(left.begin(), left.end(), right.begin(), 0.0));
  END_CPP11
}
)", file.path(pkg, "src", "dot.cpp"))
writeLines(r"(
subroutine fscale(n, x, factor)
  integer, intent(in) :: n
  double precision, intent(inout) :: x(n)
  double precision, intent(in) :: factor
  x = x * factor
end subroutine fscale
)", file.path(pkg, "src", "scale.f90"))
writeLines("PKG_LIBS = $(FLIBS)", file.path(pkg, "src", "Makevars"))

log <- system2(
  file.path(R.home("bin"), "R"),
  c("CMD", "INSTALL", "--no-docs", "--no-html", "-l", shQuote(lib), shQuote(pkg)),
  stdout = TRUE,
  stderr = TRUE
)
status <- attr(log, "status")
if (!is.null(status) && status != 0L) {
  writeLines(tail(log, 40L))
  stop("R CMD INSTALL failed with status ", status)
}
library(ds60toolchain, lib.loc = lib)
stopifnot(identical(c_sum(1:4), 10))
stopifnot(identical(cpp11_dot(c(1, 2, 3), c(4, 5, 6)), 32))
stopifnot(identical(f_scale(c(1, 2.5), 2), c(2, 5)))
cat("Installed a C, C++ (cpp11) and Fortran package into a per-job library.\n")

Rcpp::cppFunction(
  "int ds60_twice(int x) { return 2 * x; }",
  cacheDir = file.path(root, "rcpp-cache")
)
stopifnot(identical(ds60_twice(21L), 42L))
cat("Compiled and called an Rcpp function.\n")
cat("r-toolchain checks passed: C, C++ (cpp11), Fortran and Rcpp\n")
"""


class Client(Protocol):
    def call(self, action: str, **fields: Any) -> dict[str, Any]: ...


def run_probe(client: Client, *, budget: float = 150.0) -> dict[str, Any]:
    readiness = client.call("module-readiness")["profiles"]
    if not any(row["profile"] == PROFILE and row["ready"] for row in readiness):
        raise ValueError(f"The {PROFILE} worker is not ready.")
    job_id = uuid.uuid4().hex
    client.call(
        "module-run",
        lesson_id=LESSON_ID,
        source=PROBE_SOURCE,
        timeout_seconds=120,
        request_id=job_id,
        purpose="solution",
    )
    deadline = time.monotonic() + budget
    while True:
        job = client.call("module-job", job_id=job_id)
        if job["status"] in TERMINAL:
            break
        if time.monotonic() >= deadline:
            client.call("module-cancel", job_id=job_id)
            raise TimeoutError("The R toolchain probe did not finish within its budget.")
        time.sleep(0.25)
    if (
        job.get("job_id") != job_id
        or job.get("status") != "succeeded"
        or job.get("returncode") != 0
        or job.get("profile") != PROFILE
        or MARKER not in job.get("output", "")
    ):
        detail = str(job.get("output", job.get("detail", "")))[-2000:]
        raise ValueError(f"The R worker could not build a compiled package: {detail}")
    print(f"PASS: {PROFILE}: compiled package build and Rcpp in a classroom job", flush=True)
    return {
        "schema_version": 1,
        "profile": PROFILE,
        "lesson_id": LESSON_ID,
        "job_id": job_id,
        "status": job["status"],
        "elapsed_seconds": job.get("elapsed_seconds"),
        "languages": ["C", "C++ (cpp11)", "Fortran", "Rcpp"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--confirm-disposable", action="store_true")
    args = parser.parse_args(argv)
    if not args.confirm_disposable:
        parser.error("This creates a run receipt. Use --confirm-disposable on a test project.")
    result = run_probe(ClassroomClient(args.url))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
