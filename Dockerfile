FROM alpine:latest

RUN apk update \
    && apk add bash \
    && apk add python3 py3-pip \
    && apk add make cmake gcc g++ \
    && apk add qemu qemu-img qemu-system-x86_64 \
    && rm -rf /var/cache/apk/* \
    && mkdir app \
    && mkdir SWEB/ \
    && cd app/

# how to deal with ramdisk?

COPY ["src/", "app/"]
CMD ["bash", "app/compile-test.sh"]