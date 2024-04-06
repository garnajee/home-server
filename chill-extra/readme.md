# Readme

You'll find here a docker-compose to run extra dockers and scripts to update docker/package.

## Docker-compose

This docker-compose will run:

- [Removarr](https;//github.com/garnajee/removarr)
- [JellyHookAPI](https://github.com/garnajee/JellyHookAPI)
- [Jellystats](https://github.com/CyferShepard/Jellystat)

You need to modify the `.env` file.

You need to create these folders:

```
chill-extra/
   |-JellyHookAPI
   |-jellystat
   |---backup-data
   |---psql/data
```

Use this command: `mkdir -p {JellyHookAPI,jellystat/{backup-data,psql/data}}`.

To use JellyHookAPI, please refer to the [corresponding github](https://github.com/garnajee/JellyHookAPI).

Removarr will be available at `<ip>:8012`.

## Update
### whatsapp

The script must be in `/opt/chill/update-whatsapp.sh`.`

To run: `$ ./update-whatsapp.sh`.

> [!WARNING]
> You need these folder in /opt/chill :
>
> `cd /opt/chill`
> `mkdir -p backup-not-used/whatsapp/`

### docker-compose

To run: `$ sudo ./update-docker-compose.sh`.

