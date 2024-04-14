FROM alpine:latest

RUN apk update \
    && apk add bash \
    && apk add python3 py3-pip \
    && apk add make cmake gcc g++ \
    && apk add qemu qemu-img qemu-system-x86_64 \
    && rm -rf /var/cache/apk/* \
    && mkdir app \
    && mkdir SWEB/

# better extra copy for build cache
COPY ["requirements.txt", "/app/requirements.txt"]
COPY ["src/", "app/"]

WORKDIR "/app/"
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

#ENTRYPOINT ["python3", "main.py"]