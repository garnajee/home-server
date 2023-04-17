# Home Server

This is my perfect docker-compose for my streaming server.

You'll find two 2 docker-compose, one to create the streaming services and the other one to access them through a reverse proxy.

The only thing to modify is the `.env` file to suits your setup.

Here, we are going to install everything under `/opt/chill/` (full automation) and `/opt/docker/` (reverse proxy).

To install everything, just follow this Readme in this order.

## Table of Content

- [Home Server](#home-server)
  * [Table of Content](#table-of-content)
  * [Requirements](#requirements)
  * [Medias Server](#medias-server)
      + [What's inside](#what-s-inside)
      + [Installation](#installation)
        - [Modify `.env`](#modify--env-)
        - [Create a docker network](#create-a-docker-network)
      + [Run!](#run-)
      + [Check VPN connection](#check-vpn-connection)
      + [Update docker's images](#update-docker-s-images)
        - [Update one specific image](#update-one-specific-image)
        - [Update all images](#update-all-images)
      + [Access services](#access-services)
  * [Reverse Proxy](#reverse-proxy)
      + [What's inside](#what-s-inside-1)
      + [Installation](#installation-1)
      + [Run](#run)
      + [Get a domain name & SSL certificate](#get-a-domain-name---ssl-certificate)
  * [Setup all the services](#setup-all-the-services)
      + [Transmission](#transmission)
      + [Jackett](#jackett)
      + [Radarr & Sonarr](#radarr---sonarr)
      + [Jellyfin](#jellyfin)
      + [Ombi](#ombi)
  * [Bonus](#bonus)
      + [Webhooks](#webhooks)
- [License](#license)

## Requirements

* [docker](https://docs.docker.com/engine/install/)
* [docker-compose](https://docs.docker.com/compose/install/)
* a server maybe? I deployed these docker-compose on 2 servers: a Synology DS923+ and a custom server
* create docker [user](https://docs.docker.com/engine/install/linux-postinstall/)

Synology Server: 

 - Download the Docker App available on Synology Package Center
 - Create a docker [user](https://trash-guides.info/Hardlinks/How-to-setup-for/Synology/#create-a-user)
 - Connect on SSH and download `docker-compose` [latest command version](https://docs.docker.com/compose/install/other/):

```bash
$ curl -SL https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
```

 - check version: `$ docker-compose version`

## Medias Server
### What's inside

This docker-compose contains:

- [Transmission-openvpn](https://github.com/haugene/docker-transmission-openvpn)
- [Jackett](https://github.com/Jackett/Jackett)
- [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr)
- [Jellyfin](https://github.com/jellyfin/jellyfin)
- [Ombi](https://github.com/Ombi-app/Ombi)
- [Radarr](https://github.com/Radarr/Radarr)
- [Sonarr](https://github.com/Sonarr/Sonarr)
- [Removarr](https://github.com/garnajee/removarr)

### Installation

* Delete previous installation **be careful**

```bash
$ rm -rf /opt/chill
```

* Create the structure for every services

```bash
$ mkdir -p /opt/chill/{transovpn/{config,ratio},jackett/config,jellyfin/config,ombi/config,radarr/config,sonarr/config,bazarr/config,storage/downloads/{completed,incomplete,watch,medias/{films,series}}}
```

Here is what it's going to create:

```bash
opt
└── chill
    ├── jackett
    │   └── config
    ├── jellyfin
    │   └── config
    ├── ombi
    │   └── config
    ├── radarr
    │   └── config
    ├── sonarr
    │   └── config
    ├── storage
    │   └── downloads
    │       ├── completed
    │       ├── incomplete
    │       ├── medias
    │       │   ├── films
    │       │   └── series
    │       └── watch
    └── transovpn
        ├── config
        └── ratio
```

The `/opt/chill/transovpn/ratio/` folder is used to fake your upload stats on semi-private indexers.

The `/opt/chill/storage/downloads/watch/` folder is used when you manually put `.torrent` files, so it's going to be downloaded automatically without any access to the Transmission interface.

* To check everything was properly created

```bash
$ ls -lR /opt/chill
```

Download the [`docker-compose-medias.yml`](docker-compose-medias.yml) and [`.env-example`](.env-example) in `/opt/chill/`, and rename them:

```bash
$ cd /opt/chill
$ wget https://raw.githubusercontent.com/garnajee/home-server/master/docker-compose-medias.yml -O docker-compose.yml
$ wget https://raw.githubusercontent.com/garnajee/home-server/master/.env-example -O .env
```

#### Modify `.env`

Normally, you don't need to modify the docker-compose.yml file. Only the `.env` file.

- list of [VPN PROVIDERS](https://haugene.github.io/docker-transmission-openvpn/supported-providers/)
- local subnet mask for `NETWORKIP`: `ip route | awk '!/ (docker0|br-)/ && /src/ {print $1}'`

#### Create a docker network

This part is optional. It's going to be created automatically. But you can still do it manually if you want.

I did it manually because of the reverse proxy causing errors if I attached it to the automatically created docker subnet.

All these images are going to be in the same docker network. To avoid any further conflict, just create it before running the docker-compose.

Here the subnet is `10.10.66.0/24`. If you want to change this by something else, you'll need to modify the `docker-compose.yml` too. But remember, it's just a subnet *inside* docker, it's not going to affect your local network.

```bash
$ docker network rm net-chill
$ docker network create net-chill -d bridge --subnet 10.10.66.0/24
```

### Run!

For the first execution of the docker-compose, I recommend to use this command, to check if there is no errors:

Move the `docker-compose.yml` and `.env` file in `/opt/chill/`.

```bash
$ cd /opt/chill/
$ docker-compose up
```

It's going to download all the images, and start all the services.

**By the way, each request made by Jackett and FlareSolverr goes through the VPN.**

Now, if you don't see any red lines among the hundreds of lines that have just scrolled through the terminal, it's usually a good sign.

So you can now stop this by pressing `CTRL+c` (one or two times to force stop), and then run the docker-compose again, but in background this time:

```bash
$ cd /opt/chill/
$ docker-compose up -d
```

Check the status of each docker:

```bash
$ docker ps -a
```

`Status` should be `Up`.

### Check VPN connection

Now everything is up, just to be sure, you can check if Transmission goes through VPN:

```bash
$ docker exec -it transovpn curl ifconfig.co
XXX.XXX.XXX.XXX
```
And then check the location of this ip address [here](https://iplocation.com).

### Update docker's images
#### Update one specific image

To update one specific docker image:

```bash
$ cd /opt/chill
$ docker-compose stop <container_name>
$ docker-compose rm <container_name>
$ docker-compose pull <container_name>
$ docker-compose up -d
```

#### Update all images

To update all images:

```bash
$ docker-compose down
$ docker-compose pull
$ docker-compose up -d
```

### Access services

To access services: (`IP` is the ip of your server)

| **Service**          | **Address**  |
|----------------------|--------------|
| Transmission-openvpn | `<IP>:8000`  |
| Jackett              | `<IP>:8001`  |
| FlareSolverr         | `<IP>:8002`  |
| Jellyfin             | `<IP>:8003`  |
| Ombi                 | `<IP>:8004`  |
| Radarr               | `<IP>:8010`  |
| Sonarr               | `<IP>:8011`  |
| Removarr             | `<IP>:8012`  |

## Reverse Proxy

To access Jellyfin and Ombi from outside your local network, you'll need to set up a reverse proxy.

For that purpose, I'm going to use [Nginx Proxy Manager](https://nginxproxymanager.com/setup/).

You also need to open 2 ports on your router:

| Application/Service | Internal Port | External Port | Protocol | Equipment   |
|:-------------------:|:-------------:|:-------------:|:--------:|:-----------:|
| HTTP                | 8080          | 80            | TCP/UDP  | Your-Server |
| HTTPS               | 4443          | 443           | TCP/UDP  | Your-Server |


### What's inside

This docker-compose contains:

- [Nginx Proxy Manager](https://github.com/NginxProxyManager/nginx-proxy-manager)
- [Maria DB Aria](https://github.com/jc21/docker-mariadb-aria)

### Installation

* Create the directory structure

```bash
$ mkdir -p /opt/docker/{nginx-proxy-manager,npm-db}
```

Download the [`docker-compose-rp.yml`](docker-compose-rp.yml) in `/opt/docker/`, and rename it:

```bash
$ cd /opt/docker
$ wget https://raw.githubusercontent.com/garnajee/home-server/master/docker-compose-rp.yml -O docker-compose.yml
```

I didn't create a `.env` file for this docker-compose mainly as this service is not going to be exposed on the web.

Feel free to modify `user`, `password`, `name`, and so on directly in the `docker-compose.yml`.

### Run

Simply execute this:

```bash
$ cd /opt/docker/
$ docker-compose up
```

Again, it's going to download the docker images. Check if there is no error, and if it's good, hit `CTRL+c` to stop everything and run this command:

```bash
$ docker-compose up -d
```

The service will be accessible at: `<IP>:81`.

The default Admin User is:

```
email: admin@example.com
password: changeme
```

You'll be ask to change these informations after the first logging. 

### Get a domain name & SSL certificate

I bought a domain name from OVH. If you do the same, follow this:

* create an account on [OVH](https://ovh.com)
* buy a domain name
* once your domain name has been activated, create the necessary token for SSL
* use this [link](https://www.ovh.com/auth/api/createToken?GET=/domain/zone/*&POST=/domain/zone/*&PUT=/domain/zone/*&DELETE=/domain/zone/*)
+ **Make sure to write everything**

You'll need something like this:

```
dns_ovh_endpoint = ovh-eu
dns_ovh_application_key = 1091757595XXXXXa
dns_ovh_application_secret = a1z2g3y435TGcazbXXXXXXXXa45e
dns_ovh_consumer_key = agf6hU1g13uj86XXXXXXXXXfv1l2n3g4j
```

* To create your certificate, go back on NPM (`<IP>:81`), "SSL Certificates" tab, "Add ..."
* fill the information for: `*.yourdomain.com` and `yourdomain.com`

## Setup all the services
### Transmission

Nothing to setup or maybe the "Speed Limits" depending on your internet connection.

### Jackett

Check the box: 

- External access
- Cache enabled (recommended)

Add these values:

- "Cache TTL (seconds):" `2100`
- "Cache max results per indexer:" `1000`
- "FlareSolverr API URL:" `http://10.10.66.102:8191`    # **if you don't change anything on the docker-compose, that's it**
- "FlareSolverr Max Timeout (ms):" `100000`

Leave the rest blank.

Add your indexer(s).

### Radarr & Sonarr

Follow these [guides](https://trash-guides.info/).

I'll add more information later.

### Jellyfin

Follow the steps, it's easy.

Create an API key for Ombi.

Create all the users who are going to access to Jellyfin **and** Ombi.

### Ombi

In the setting page:

+ "Configuration" tab:
  - (General) base URL: `/ombi`
  - (User Management) check the box. It means, that the Jellyfin account (user/password) is the same for Ombi.

+ "Media Server" tab:
  - Hostname/IP: put the internal docker ip: `10.10.66.103`.
  - Port: `8096`
  - API key: the one you created just before
  - then load libraries, submit.

Now for every service you're going to add (Sonarr, Radarr, ...) make sure to write the *internal docker ip address and internal port of the application*. The API keys are available in Sonarr/Radarr/... settings tab.

## Bonus

Don't want to use a reverse proxy?

You can use a VPN:

- Official Synology VPN package -> *need to open port on your router*

And if you don't want to open port on your router (or if you can't):

- [Tailscale](https://tailscale.com/kb/1131/synology/) on Synology 
- [CloudFlare Tunnel](https://github.com/cloudflare/cloudflared)

Pay attention to not use CloudFlare tunnel for Jellyfin streaming, you may be banned for breaking TOS [term 2.8](https://www.cloudflare.com/en-gb/terms/).

### Webhooks

I provide some webhooks for Jellyfin. These webhooks are used for Discord and MS Teams.

# License

This project is under [MIT](LICENSE) License.
