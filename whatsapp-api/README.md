# WhatsApp API

In order to send a (Jellyfin) webhook to a WhatsApp contact or group, I will use this [API](https://github.com/aldinokemal/go-whatsapp-web-multidevice).

To see the documentation of this API, please refer to the [official documentation](https://github.com/aldinokemal/go-whatsapp-web-multidevice/blob/main/docs/openapi.yaml).
To have a better view of the API, you can use the [Swagger Editor](https://editor.swagger.io/?url=https://raw.githubusercontent.com/aldinokemal/go-whatsapp-web-multidevice/main/docs/openapi.yaml).

## Installation

Luckily, I've already done all the following steps and you just have to clone the original repository, modify the [`.env`](.env) file, build and run the container.

And finally, connect to the web interface: `http://<ip>:8888`, then connect to your WhatsApp account and retrieve the necessary information to configure the JellyHookAPI Python script.

Just to be clear:

- the `.env` file need to be at the root of this repository,
- the `docker-compose.yml` file need to be at the root of this repository,
- and the `golang.Dockerfile` file need to be in the `docker` folder

These are the only files modified from the original repository.

To install this API, you'll need to:

- clone the repository: `git clone https://github.com/aldinokemal/go-whatsapp-web-multi-device`
- change directory: `cd go-whatsapp-web-multi-device`
- modify the `docker-compose.yml` to connect the container to the internal docker subnet => [see this](#connect-the-container-to-the-internal-docker-subnet)
- (optionnal) modify the Dockerfile and docker-compose.yml to add basic http authentication => [see this](#add-basic-http-authentication)
- build and run the container: `docker-compose up -d --build`
- connect to the web interface: `http://<ip>:8888`.

### Connect the container to the internal docker subnet

You need to modify the docker-compose.yml to be able to connect this container to the others and vice-versa.

To do so, add the following lines to the `docker-compose.yml`:

```yml
...
  whatsapp_go:
    ...
    networks:
      net-chill:
        ipv4_address: 10.10.66.200

networks:
  net-chill:
    external: true
    driver: bridge
    ipam:
      config:
        - subnet: 10.10.66.0/24
```

### Add basic http authentication

To add basic http authentication, you'll need to:

- modify the [`docker/golang.Dockerfile`](golang.Dockerfile) and change the last line:

```diff
- ENTRYPOINT ["/app/whatsapp"]
+ ENTRYPOINT ["/app/whatsapp", "-b=user:passWithoutDash"]
```

*special caracters in password seems to bug...*

- modify the [`docker-compose.yml`](docker-compose.yml):

```yml
    ...
    ports:
      - "0.0.0.0:8888:3000"
    ...
```

