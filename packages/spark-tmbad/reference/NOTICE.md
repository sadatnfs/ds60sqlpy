# Source and dependency notices

The R/Python orchestration, mathematical references and four C++ model templates
in this directory are original DS60 source under the MIT license in `LICENSE`.
They do not reproduce the implementation of AFModel or glmmTMB.

The optional environment installs the real glmmTMB package from commit
`1db3b4692aa4c61ae5c9974b32b9f91555cf5f2c`, development version1.1.15.9000,
whose DESCRIPTION declares **AGPL-3**. Its code and compiled library retain those
terms. The GNU license text is retained in `licenses/AGPL-3.0.txt`; preparation
retains the exact complete upstream source archive and extracted package source.
The dependency lock binds the archive SHA256. This is an upstream reference
integration, not a native TMBad port and not an MIT relicensing of glmmTMB.

TMB 1.9.25 is GPL-2; RTMB and RcppEigen retain their separately declared license
terms. Every CRAN dependency's declared license is recorded in the lock, and
preparation retains every downloaded source archive. Corresponding upstream
notices remain inside those archives and installed libraries. Original-template
licensing does not replace the licenses of TMB headers or linked dependencies.

The scientific inspiration for the original panel example is AFModel commit
`5362baf5aa909d9792e0aeef2b9d17c8670841b9`, MIT-licensed, authored by Nafis Sadat.
Its panel trends, effects, lag structure and variance schedules motivated the
questions. No historical operational helper, database access, infrastructure,
private data or AFModel implementation was copied or executed. The new model
states its own exact Gaussian covariance and conditional forecast distribution.

The original package's primary JVM-to-TMBad path remains independent of R. This
optional reference explicitly requires R, TMB and glmmTMB. Installing or reading
it does not extend the primary native registry's model support or qualification.
