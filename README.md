# Home Server

> [!CAUTION]
> **Disclaimer:** *The author and contributors do not claim ownership of any services listed or used in this repository and are not legally responsible for any improper or illegal use. It is provided for educational purposes only. The repository does not endorse piracy or copyright infringement. Creating a media platform based on torrents may involve downloading copyrighted content, which, without proper authorization, may be illegal in many jurisdictions. All rights go to the owners of the software used.*

This is my Docker setup for a complete media server.

The primary method now uses **two Docker Compose files**:

- `docker-compose-internal.yml` for internal automation and VPN-bound services
- `docker-compose-public.yml` for user-facing services

I switched from `transmission-openvpn` to `qbittorrent + gluetun` because:

- VPN and torrent client are now independent and easier to maintain
- Gluetun is actively maintained and more flexible
- qBittorrent is better for large torrent libraries (tags, categories, priorities, queueing)
- Internal updates can be done without disrupting Jellyfin/Seerr users

> [!NOTE]
> I've also created a [`chill-extra`](chill-extra) folder that can send WhatsApp notifications when media is added in Jellyfin, add [removarr](https://github.com/garnajee/removarr), and provide helper scripts.

> [!IMPORTANT]
> The legacy method (single compose + `transmission-openvpn`) is still available in this guide.

## Table of Contents

- [Home Server](#home-server)
  * [Table of Contents](#table-of-contents)
  * [Requirements](#requirements)
  * [Media Server (Recommended: split internal/public)](#media-server-recommended-split-internalpublic)
      + [What's inside](#whats-inside)
      + [Installation](#installation)
        - [Modify `.env`](#modify-env)
        - [Create a docker network](#create-a-docker-network)
      + [Run](#run)
      + [Check VPN connection](#check-vpn-connection)
      + [Update docker images](#update-docker-images)
      + [Access services](#access-services)
  * [Legacy setup (single compose + Transmission)](#legacy-setup-single-compose--transmission)
  * [Reverse Proxy](#reverse-proxy)
      + [What's inside](#whats-inside-1)
      + [Installation](#installation-1)
      + [Run](#run-1)
      + [Get a domain name & SSL certificate](#get-a-domain-name--ssl-certificate)
  * [Setup all services](#setup-all-services)
      + [qBittorrent](#qbittorrent)
        - [qBittorrent reference config (troubleshooting)](#qbittorrent-reference-config-troubleshooting)
      + [Radarr & Sonarr](#radarr--sonarr)
      + [Prowlarr](#prowlarr)
      + [Jellyfin](#jellyfin)
      + [Seerr](#seerr)
  * [Bonus](#bonus)
      + [Webhooks](#webhooks)
      + [Fake Ratio](#fake-ratio)
- [License](#license)

## Requirements

- [docker](https://docs.docker.com/engine/install/)
- [docker-compose](https://docs.docker.com/compose/install/)
- a server (tested on Synology DS923+ and a custom Linux server)
- create a dedicated docker [user](https://docs.docker.com/engine/install/linux-postinstall/)

Synology:

- Install Docker/Container Manager from Synology Package Center
- Create a docker [user](https://trash-guides.info/Hardlinks/How-to-setup-for/Synology/#create-a-user)
  - then run `id <username>` and note `uid`/`gid` as `PUID`/`PGID` for your `.env`
- Install latest compose plugin if needed
  - or use [`chill-extra/update-docker-compose.sh`](chill-extra/update-docker-compose.sh)
- Check version: `docker compose version` (or `docker-compose version`)

## Media Server (Recommended: split internal/public)

### What's inside

`docker-compose-internal.yml`:

- [Gluetun](https://github.com/qdm12/gluetun)
- [qBittorrent](https://www.qbittorrent.org/)
- [Prowlarr](https://github.com/Prowlarr/Prowlarr)
- [Radarr](https://github.com/Radarr/Radarr)
- [Sonarr](https://github.com/Sonarr/Sonarr)

`docker-compose-public.yml`:

- [Jellyfin](https://github.com/jellyfin/jellyfin)
- [Seerr](https://github.com/seerr-team/seerr)

### Installation

Create folders:

```bash
mkdir -p /opt/chill/{qbit,prowlarr,radarr,sonarr,jellyfin,seerr}/config
mkdir -p /opt/chill/storage/downloads/{watch,completed,incomplete,medias/{movies,series}}
```

Download files in `/opt/chill/`:

```bash
cd /opt/chill
wget https://raw.githubusercontent.com/garnajee/home-server/master/docker-compose-internal.yml -O docker-compose-internal.yml
wget https://raw.githubusercontent.com/garnajee/home-server/master/docker-compose-public.yml -O docker-compose-public.yml
wget https://raw.githubusercontent.com/garnajee/home-server/master/.env-example -O .env
```

#### Modify `.env`

You usually only need to edit `.env`:

- `WG_PRV_KEY`
- `WG_SERVER_COUNTRIES`
- `QBIT_WEBUI_PORT`
- `BASE`, `DOWNLOADS`
- `PUID`, `PGID`
- `TZ`
- `NETWORKIP` (detect with `ip route | awk '!/ (docker0|br-)/ && /src/ {print $1}'`)

Example:

```env
# VPN
WG_PRV_KEY="YOUR_WIREGUARD_PRIVATE_KEY"
WG_SERVER_COUNTRIES="Country"
QBIT_WEBUI_PORT=8088

# the rest is unchanged
BASE=/opt/chill
DOWNLOADS=/opt/chill/storage/downloads
PUID=1030
PGID=100
TZ=Europe/Paris
NETWORKIP=192.168.1.0/24
```

#### Create a docker network

Optional (it can be auto-created), but manual creation is recommended:

```bash
docker network rm net-chill
docker network create net-chill -d bridge --subnet 10.10.66.0/24
```

### Run

Run internal stack:

```bash
cd /opt/chill
docker compose -f docker-compose-internal.yml up -d
```

Run public stack:

```bash
docker compose -f docker-compose-public.yml up -d
```

Check containers:

```bash
docker compose -f docker-compose-internal.yml ps -a
docker compose -f docker-compose-public.yml ps -a
```

### Check VPN connection

```bash
docker exec -it gluetun wget -qO- https://ifconfig.co
```

Then check the location of that IP (for example on [ifconfig.co](https://ifconfig.co)).

### Update docker images

Update internal stack only:

```bash
docker compose -f docker-compose-internal.yml pull
docker compose -f docker-compose-internal.yml up -d
```

Update public stack only:

```bash
docker compose -f docker-compose-public.yml pull
docker compose -f docker-compose-public.yml up -d
```

### Access services

| **Service**       | **Address**               |
|-------------------|---------------------------|
| qBittorrent WebUI | `<IP>:${QBIT_WEBUI_PORT}` |
| Prowlarr          | `<IP>:8001`               |
| Jellyfin          | `<IP>:8003`               |
| Seerr             | `<IP>:8004`               |
| Radarr            | `<IP>:8010`               |
| Sonarr            | `<IP>:8011`               |

## Legacy setup (single compose + Transmission)

This method is still supported.

```bash
cd /opt/chill
wget https://raw.githubusercontent.com/garnajee/home-server/master/docker-compose-medias.yml -O docker-compose-medias.yml
wget https://raw.githubusercontent.com/garnajee/home-server/master/.env-example-legacy -O .env
docker compose -f docker-compose-medias.yml up -d
```

This is no longer the recommended default.

## Reverse Proxy

To access Jellyfin and Seerr outside your local network, use a reverse proxy.
In this guide, we use [Nginx Proxy Manager](https://nginxproxymanager.com/setup/).

You need to open 2 ports on your router:

| Application/Service | Internal Port | External Port | Protocol | Equipment   |
|:-------------------:|:-------------:|:-------------:|:--------:|:-----------:|
| HTTP                | 8080          | 80            | TCP/UDP  | Your-Server |
| HTTPS               | 4443          | 443           | TCP/UDP  | Your-Server |

### What's inside

- [Nginx Proxy Manager](https://github.com/NginxProxyManager/nginx-proxy-manager)
- [Maria DB Aria](https://github.com/jc21/docker-mariadb-aria)

### Installation

Create folders:

```bash
mkdir -p /opt/docker/{nginx-proxy-manager,npm-db}
```

Download compose file:

```bash
cd /opt/docker
wget https://raw.githubusercontent.com/garnajee/home-server/master/docker-compose-rp.yml -O docker-compose.yml
```

### Run

```bash
cd /opt/docker
docker compose up -d
```

Service URL: `<IP>:81`

Default admin:

```txt
email: admin@example.com
password: changeme
```

### Get a domain name & SSL certificate

I use OVH:

- create an account on [OVH](https://ovh.com)
- buy a domain name
- create the token for SSL automation:
  - https://www.ovh.com/auth/api/createToken?GET=/domain/zone/*&POST=/domain/zone/*&PUT=/domain/zone/*&DELETE=/domain/zone/*

You'll get values like:

```txt
dns_ovh_endpoint = ovh-eu
dns_ovh_application_key = xxxxxxxxxxxxx
dns_ovh_application_secret = xxxxxxxxxxxxx
dns_ovh_consumer_key = xxxxxxxxxxxxx
```

In NPM:

- go to `SSL Certificates`
- add wildcard + root domain: `*.yourdomain.com` and `yourdomain.com`

## Setup all services

### qBittorrent

Configure categories, tags, queueing, and priorities to match your workflow.

#### qBittorrent reference config (troubleshooting)

If users run into issues, they can compare with this known working reference:

- [`qBittorrent.conf`](qBittorrent.conf)

### Radarr & Sonarr

Follow [TRaSH guides](https://trash-guides.info/).

If you want similar quality profiles/custom formats, see [`recyclarr-setup`](recyclarr-setup).

### Prowlarr

Add indexers, then connect apps in `Settings > Apps`:

- Prowlarr: `http://10.10.66.100:9696`
- Radarr: `http://10.10.66.110:7878`
- Sonarr: `http://10.10.66.111:8989`

### Jellyfin

Follow initial setup wizard and create users.

For custom menu links:

```txt
- ${BASE}/jellyfin/web-config.json:/usr/share/jellyfin/web/config.json
```

Read more: [Jellyfin web config](https://jellyfin.org/docs/general/clients/web-config/#custom-menu-links).

### Seerr

Sign in with Jellyfin account and use internal Docker IPs for Jellyfin/Radarr/Sonarr connections.

## Bonus

Do not want to expose ports?

- Official Synology VPN package (requires router port-forwarding)
- [Tailscale](https://tailscale.com/kb/1131/synology/) on Synology
- [CloudFlare Tunnel](https://github.com/cloudflare/cloudflared)

> [!WARNING]
> Be careful with CloudFlare Tunnel for Jellyfin streaming, it can violate [Cloudflare ToS](https://www.cloudflare.com/en-gb/terms/).

### Webhooks

Jellyfin webhook templates are available for:

- Generic API: [`webhooks/jellyfin/global-item.handlebars`](webhooks/jellyfin/global-item.handlebars)
- Discord: [`webhooks/jellyfin/discord`](webhooks/jellyfin/discord)
- Microsoft Teams: [`webhooks/jellyfin/ms-teams`](webhooks/jellyfin/ms-teams)

Install plugin first: Jellyfin `Dashboard > Plugins > Catalog > Webhook`.

Restart Jellyfin:

```bash
cd /opt/chill
docker compose -f docker-compose-public.yml restart jellyfin
```

For WhatsApp workflow examples, see [`whatsapp-api`](whatsapp-api).

### Fake Ratio

If you need to fake upload ratio on private trackers, you can use [Ratio.py](https://github.com/garnajee/Ratio.py).

> [!CAUTION]
> Not recommended for long-term usage. Consider seeding fairly.

When using the legacy Transmission container, you can run the script there so traffic stays behind VPN.

# License

This project is under [MIT](LICENSE) License.

