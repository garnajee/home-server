# Home Server

> [!CAUTION]
> **Disclaimer:** *The author and contributors do not claim ownership of any services listed or used in this repository and are not legally responsible for any improper or illegal use. It is provided for educational purposes only. The repository does not endorse piracy or copyright infringement. Creating a media platform based on torrents may involve downloading copyrighted content, which, without proper authorization, may be illegal in many jurisdictions. All rights go to the owners of the software used.*

This is my perfect docker-compose for my streaming server.

You'll find two 2 docker-compose, one to create the streaming services and the other one to access them through a reverse proxy.

> [!NOTE]
> I've also created a `chill-extra` folder that automatically sends notifications on WhatsApp as soon as media is added in Jellyfin and add the [removarr](https://github.com/garnajee/removarr) docker.


> [!IMPORTANT]
> The only thing to modify is the `.env` file to suits your setup.

Here, we are going to install everything under `/opt/chill/` (full streaming automation) and `/opt/docker/` (reverse proxy).

To install everything, just follow this Readme in this order.

## Table of Contents

- [Home Server](#home-server)
  * [Table of Content](#table-of-contents)
  * [Requirements](#requirements)
  * [Medias Server](#medias-server)
      + [What's inside](#whats-inside)
      + [Installation](#installation)
        - [Modify `.env`](#modify-env)
        - [Create a docker network](#create-a-docker-network)
      + [Run!](#run)
      + [Check VPN connection](#check-vpn-connection)
      + [Update docker's images](#update-dockers-images)
        - [Update one specific image](#update-one-specific-image)
        - [Update all images](#update-all-images)
      + [Access services](#access-services)
  * [Reverse Proxy](#reverse-proxy)
      + [What's inside](#whats-inside-1)
      + [Installation](#installation-1)
      + [Run](#run)
      + [Get a domain name & SSL certificate](#get-a-domain-name--ssl-certificate)
  * [Setup all the services](#setup-all-the-services)
      + [Transmission-openvpn](#transmission-openvpn)
      + [Radarr & Sonarr](#radarr--sonarr)
        - [Radarr/Sonarr Settings](#radarrsonarr-settings)
      + [Prowlarr](#prowlarr)
      + [Jellyfin](#jellyfin)
      + [Jellyseerr](#jellyseerr)
  * [Bonus](#bonus)
      + [Webhooks](#webhooks)
	    - (to send to discord, Microsoft Teams or any API)
      + [Fake Ratio](#fake-ratio)
- [License](#license)

## Requirements

* [docker](https://docs.docker.com/engine/install/)
* [docker-compose](https://docs.docker.com/compose/install/)
* a server maybe? I deployed these docker-compose on 2 servers: a Synology DS923+ and a custom server
* create docker [user](https://docs.docker.com/engine/install/linux-postinstall/)

Synology Server: 

- Download the Docker App available on Synology Package Center
- Create a docker [user](https://trash-guides.info/Hardlinks/How-to-setup-for/Synology/#create-a-user)
  - once it's done, connect on SSH and type `id <username>` and write down the `uid` and `gid` respectively `PUID` and `PGID` for the [`.env`](.env-example).
- Connect on SSH and download `docker-compose` [latest command version](https://docs.docker.com/compose/install/other/):
  - or use my custom script to [download the latest docker-compose release](update-docker-compose.sh)

- check version: `$ docker-compose version`

## Medias Server
### What's inside

This docker-compose contains:

- [Transmission-openvpn](https://github.com/haugene/docker-transmission-openvpn)
- [Prowlarr](https://github.com/Prowlarr/Prowlarr)
- [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr)
- [Jellyfin](https://github.com/jellyfin/jellyfin)
- [Jellyseerr](https://github.com/Fallenbagel/jellyseerr)
- [Radarr](https://github.com/Radarr/Radarr)
- [Sonarr](https://github.com/Sonarr/Sonarr)

### Installation

* Delete previous installation **be careful**

```bash
$ rm -rf /opt/chill
```

* Create the structure for every services

```bash
$ mkdir -p /opt/chill/{transovpn/{config},prowlarr/config,jellyfin/config,jellyseerr/config,radarr/config,sonarr/config,storage/downloads/{completed,incomplete,watch,medias/{movies,series}}}
```

Here is what it's going to create:

```bash
opt
└── chill
    ├── jellyfin
    │   └── config
    ├── jellyseerr
    │   └── config
    ├── prowlarr
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
    │       │   ├── movies
    │       │   └── series
    │       └── watch
    └── transovpn
        └── config
```


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
- local subnet mask for `NETWORKIP` (use this command to know yours) : `ip route | awk '!/ (docker0|br-)/ && /src/ {print $1}'`
- PUID and PGID
- TZ

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

**By the way, each request made by Prowlarr and FlareSolverr goes through the VPN.**

Now, if you don't see any red lines among the hundreds of lines that have just scrolled through the terminal, it's usually a good sign.

So you can now stop this by pressing `CTRL+c` (one or two times to force stop), and then run the docker-compose again, but in background this time:

```bash
$ cd /opt/chill/
$ docker-compose up -d
```

Check the status of each docker:

```bash
$ docker-compose ps -a
```

`Status` should be `Up`.

### Check VPN connection

Now everything is up, just to be sure, you can check if Transmission goes through VPN:

```bash
$ docker exec -it transovpn curl ifconfig.co
XXX.XXX.XXX.XXX
```
And then check the location of this ip address [here](https://ifconfig.co) for example.

You can do the same command (just to be sure) for Prowlarr and Flaresolverr, they have the same ip address.

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
| Prowlarr             | `<IP>:8001`  |
| FlareSolverr         | `<IP>:8002`  |
| Jellyfin             | `<IP>:8003`  |
| Jellyseerr           | `<IP>:8004`  |
| Radarr               | `<IP>:8010`  |
| Sonarr               | `<IP>:8011`  |

## Reverse Proxy

To access Jellyfin and Jellyseerr from outside your local network, you'll need to set up a reverse proxy.

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
dns_ovh_application_key = 109XXX7595XXXXXa
dns_ovh_application_secret = a1z2g3y435TGcazbXXXXXXXXa45e
dns_ovh_consumer_key = agf6hU1g13uj86XXXXXXXXXfv1l2n3g4j
```

* To create your certificate, go back on NPM (`<IP>:81`), "SSL Certificates" tab, "Add ..."
* fill the information for: `*.yourdomain.com` and `yourdomain.com`

## Setup all the services
### Transmission-openvpn

Nothing to setup or maybe the "Speed Limits" depending on your internet connection.

### Radarr & Sonarr

Follow these [guides](https://trash-guides.info/).

I create a config to prefer download WEB-DL - MULTi (Original language + Truefrench) - 1080p - h264 - and NO HDR/10 bit.

If you want to have the same config, see the [`recyclarr-setup`](recyclarr-config) folder.

#### Radarr/Sonarr Settings

1. Media Management:
    - check `Replace Illegal Characters`
    - Colon Replacement: `Delete`
    - Path `/downloads/medias/movies` (for sonarr: `/downloads/medias/series`)
2. Profiles : make
3. Quality: Not changed
4. Custom Formats: automatically imported with recyclarr
5. Indexer: it'll be added automatically with Prowlarr
6. Download Client:
    - add transmission
    - host: 10.10.66.100
    - port: 9091
    - set username and password
    - recent priority: `last`
    - older priority: `last`
    - check `Remove Completed`
    - `Remote Path Mappings`: Host: `10.10.66.100 (Transmission)` ; Remote Path: `/data/completed` ; Local Path: `/data/completed`

> [!IMPORTANT]
> Go under `settings/general` and copy the API key, you'll need it for Prowlarr

### Prowlarr

Add your indexer. In `Tags` field, add "flaresolverr".

In order to add `Flaresolverr` proxy:

- go to `Settings > Indexers`
- add "Flaresolverr" 
- make sure the tag is "flaresolverr"
- add this ip address: "http://10.10.66.100:8191"
- save

Connect to Radarr/Sonarr:

- go to `Settings > Apps`
- add radarr:
  - full sync
  - prowlarr server: http://10.10.66.100:9696
  - radarr server: http://10.10.66.110:7878

### Jellyfin

Follow the steps, it's easy.

Create all the users who are going to access to Jellyfin **and** Jellyseerr.

To have better images for your libraries, you can use [these images](https://imgur.com/a/Guqk15B).

**Prevent users from changing their password:**

Go into *Dashboard* > *General* > scroll down to the *CSS* section and add this CSS code:

```css
.updatePasswordForm {
  display: none !important;
}
```

**Add a custom button in the menu**

You can add a custom button to the Jellyfin menu. For example, you can add a link to Jellyseerr.

To do that, you need to add this line in the Jellyfin's `volume` field in the docker-compose file:

```
- ${BASE}/jellyfin/web-config.json:/usr/share/jellyfin/web/config.json
```

And add the `web-config.json` file in your `/opt/chill/jellyfin/` folder.

*You'll see that the docker path is not the same as in the documentation. I don't know why, but that's the only way I can get it to work.*

Read more [here](https://jellyfin.org/docs/general/clients/web-config/#custom-menu-links).

### Jellyseerr

Follow the steps, it's easy.

Sign in with your Jellyfin account and make sure to use the jellyfin *internal docker ip address* for the "Jellyfin URL".

When Syncing Librairies, uncheck "Collections".

Then, add your radarr and sonarr server (still with the internal docker ip address).

Once this is done, you can sync Jellyfin users with Jellyseerr, so that they have the same account for Jellyfin and Jellyseerr.

For sonarr server settings, make sure to check *Season folder*.

## Bonus

Don't want to use a reverse proxy?

You can use a VPN:

- Official Synology VPN package -> *need to open port on your router*

And if you don't want to open port on your router (or if you can't):

- [Tailscale](https://tailscale.com/kb/1131/synology/) on Synology
- [CloudFlare Tunnel](https://github.com/cloudflare/cloudflared)

> [!WARNING]
> Pay attention to not use CloudFlare tunnel for Jellyfin streaming, you may be banned for breaking [TOS](https://www.cloudflare.com/en-gb/terms/).

### Webhooks

I provide some webhooks for Jellyfin. These webhooks are used for:

- [Any API (WhatsApp in my case)](#any-api-link)
- [Discord](#discord-webhook)
- [Microsoft Teams](#ms-teams-webhook)

First of all, you need to install the Jellyfin plugin called "Webhooks": Jellyfin > Dashboard > Plugins > Catalog > Webhook

Then, you need to restart Jellyfin:

```bash
$ cd /opt/chill/
$ docker-compose restart jellyfin
```

Now, go back to Jellyfin in the Plugins tab and click on Webhook.

The "*Server Url*" is your Jellyfin URL. If you expose it on internet, it's something like this: https://jellyfin.yourdomainname.com/

*If you don't have a domain name, Jellyfin will not be able to display images (posters) in the Discord/Teams webhooks.*

<details close>
  <summary id="any-api-link">Any API</summary>
    <p>This method will allow you to send a webhook to any service/api you want in a very easy way.</p>
    <p>This consists of using your own API and create your request in Python (which is more flexible than the Jellyfin Webhook plugin) and send it to the API you want.</p>
    <h5>Steps:</h5>
    <ol>
      <li>
        <b>Modify the <em>jellyhookapi.py</em> file:</b><br>
        You'll need to customize the <a href="https://github.com/garnajee/JellyfinAPI/blob/master/jellyhookapi.py">JellyHookAPI/jellyhookapi.py</a> file according to your specific needs.
      </li>
      <li>
        <b>Add the Handlebars template:</b><br>
        Navigate to Jellyfin > Plugin > Webhook > "Generic Destination" and add the <a href="webhooks/jellyfin/global-item.handlebars">Handlebars template</a>.
      </li>
      <li>
        <b>Build and run the Docker image:</b><br>
        For detailed instructions on building and running the Docker image, refer to the <a href="https://github.com/garnajee/JellyHookAPI/tree/master#jellyhookapi">JellyHookAPI/README</a> in the JellyHookAPI folder.
      </li>
    </ol>
</details>

<details close>
  <summary id="discord-webhook">Discord Webhook</summary>
    <p>To add a <strong>Discord</strong> webhook:</p>
    <ul>
      <li>click on "Add Discord Destination"</li>
      <li>"<em>Webhook Name</em>": what you want</li>
      <li>"<em>Webhook Url</em>": the discord webhook url</li>
      <li>"<em>Notification type</em>":</li>
    <ol>
      <li>if you want to receive notification when a new item (movie/tv show/...) is added, check "<em>Item Added</em>"</li>
      <li>or when a user is locked out (because of too much wrong password during connection), check "<em>User Locked Out</em>"</li>
      <li>or when a user is created/deleted, when a password is changed, ... (for every use case check <a href="webhooks/jellyfin/discord/discord-users.handlebars">this file</a>), check "<em>Authentication</em>" and "<em>User</em>"</li>
    </ol>
    <li>"<em>User Filter</em>": personally, I don't check anything here</li>
    <li>"<em>Item Type</em>": check everything (depending on your webhook template) <strong>except</strong> "<em>Send All Properties</em>"</li>
    <li>"<em>Template</em>": (copy and paste the content)</li>
    <ol>
      <li><a href="webhooks/jellyfin/discord/discord-item.handlebars">webhooks/jellyfin/discord/discord-item.handlebars</a></li>
      <li><a href="webhooks/jellyfin/discord/discord-users-locked-out.handlebars">webhooks/jellyfin/discord/discord-users-locked-out.handlebars</a></li>
      <li><a href="webhooks/jellyfin/discord/discord-users.handlebars">webhooks/jellyfin/discord/discord-users.handlebars</a></li>
    </ol>
    <li>"<em>Avatar Url</em>": just change the avatar profile picture directly on Discord</li>
    <li>"<em>Webhook Username</em>": should not be empty, but you can write what you want, the real username is defined directly in Discord</li>
    <li>"<em>Mention Type</em>": I never used this</li>
    <li>"<em>Embed Color</em>": color of the embedded message</li>
  </ul>
  <p>Then click save.</p>
</details>

<details close>
  <summary id="ms-teams-webhook">Microsoft Teams Webhook</summary>
  <p>To add a <strong>Microsoft Teams</strong> webhook:</p>
  <ul>
    <li>click on "Add a Generic Destination"</li>
    <li>check the steps for Discord, it's the same</li>
    <li>"<em>Template</em>":</li>
    <ol>
      <li>"<em>Item Added</em>": <a href="webhooks/jellyfin/ms-teams/teams-items.handlebars">webhooks/jellyfin/ms-teams/teams-items.handlebars</a></li>
      <li>"<em>User Locked Out</em>": <a href="webhooks/jellyfin/ms-teams/teams-users-locked-out.handlebars">webhooks/jellyfin/ms-teams/teams-users-locked-out.handlebars</a></li>
      <li>"<em>User</em>": <a href="webhooks/jellyfin/ms-teams/teams-users.handlebars">webhooks/jellyfin/ms-teams/teams-users.handlebars</a></li>
    </ol>
  </ul>
</details>

### Fake Ratio

If you need to fake your upload in order to have a ratio >= 1, you can use [Ratio.py](https://github.com/garnajee/Ratio.py).

I don't recommend using this indefinitely, please consider sharing to the community.

# License

This project is under [MIT](LICENSE) License.
