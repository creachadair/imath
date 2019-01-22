# Build IMath and run tests with GCC on Linux.
#
# Usage (from the imath root):
#
#   docker run --rm -it -v $PWD:/imath "$(docker build -q tests/linux)"
#
FROM alpine:latest AS base

RUN apk add --no-cache bash build-base gcc gmp-dev make python2

FROM base AS test
VOLUME  /imath
WORKDIR /imath
CMD make distclean examples check
