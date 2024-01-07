FROM alpine:latest

RUN apk update \
    && apk add bash \
    && apk add python3 py3-pip \
    && apk add make cmake gcc g++ \
    && apk add qemu qemu-img qemu-system-x86_64 \
    && rm -rf /var/cache/apk/* \
    && mkdir app \
    && mkdir SWEB/

# how to deal with ramdisk?

COPY ["src/", "app/"]
#COPY ["stdout", "/"]
#COPY ["stderr", "/"]
#CMD ["bash", "app/compile-test.sh"]
WORKDIR "/app/"
ENTRYPOINT ["python3", "main.py"]