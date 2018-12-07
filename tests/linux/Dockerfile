# Build IMath and run tests with GCC on Linux.
#
# Usage (from the imath root):
#   docker build -f tests/linux/Dockerfile .
#
FROM alpine:3.8

RUN apk add --no-cache build-base gcc make
WORKDIR /imath
ADD . .
RUN make distclean test examples
