FROM alpine:3.4

RUN apk add --update python py-boto

RUN mkdir -p /app

COPY removeVault.py /app/

WORKDIR /app

ENTRYPOINT ["python", "/app/removeVault.py"]
