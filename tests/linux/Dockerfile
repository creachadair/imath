# Build IMath and run tests with GCC on Linux.
#
# Usage (from the imath root):
#   docker build -f tests/linux/Dockerfile .
#
FROM alpine:3.8 AS base

RUN apk add --no-cache build-base gcc make

FROM base AS test
WORKDIR /imath
ADD . .
RUN make distclean test examples
