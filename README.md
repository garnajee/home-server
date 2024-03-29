# Home Server

> **Disclaimer:** *The author and contributors do not claim ownership of any services listed or used in this repository and are not legally responsible for any improper or illegal use. It is provided for educational purposes only. The repository does not endorse piracy or copyright infringement. Creating a media platform based on torrents may involve downloading copyrighted content, which, without proper authorization, may be illegal in many jurisdictions. All rights go to the owners of the software used.*

This is my perfect docker-compose for my streaming server.

You'll find two 2 docker-compose, one to create the streaming services and the other one to access them through a reverse proxy.

The only thing to modify is the `.env` file to suits your setup.

Here, we are going to install everything under `/opt/chill/` (full automation) and `/opt/docker/` (reverse proxy).

To install everything, just follow this Readme in this order.

## Table of Contents

- [Home Server](#home-server)
  * [Table of Content](#table-of-content)
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
      + [Transmission](#transmission)
      + [Jackett](#jackett)
      + [Radarr & Sonarr](#radarr--sonarr)
      + [Jellyfin](#jellyfin)
      + [Jellyseerr](#jellyseerr)
  * [Bonus](#bonus)
      + [Webhooks](#webhooks)
        - [Global Webhook](#global-webhook)
          * [Discord Webhook](#discord-webhook)
          * [Microsoft Teams Webhook](#microsoft-teams-webhook)
          * [(old method) WhatsApp Webhook](#old-method-whatsapp-webhook)
          * [(new method) WhatsApp Webhook](#new-method-whatsapp-webhook)
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
- [Jackett](https://github.com/Jackett/Jackett)
- [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr)
- [Jellyfin](https://github.com/jellyfin/jellyfin)
- [Jellyseerr](https://github.com/Fallenbagel/jellyseerr)
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
$ mkdir -p /opt/chill/{transovpn/{config,ratio},jackett/config,jellyfin/config,jellyseerr/config,radarr/config,sonarr/config,bazarr/config,storage/downloads/{completed,incomplete,watch,medias/{movies,series}}}
```

Here is what it's going to create:

```bash
opt
└── chill
    ├── jackett
    │   └── config
    ├── jellyfin
    │   └── config
    ├── jellyseerr
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
        ├── config
        └── ratio
```

The `/opt/chill/transovpn/ratio/` folder is used to fake your upload stats on (semi-)private indexers. See [Fake Ratio](#fake-ratio).

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
And then check the location of this ip address [here](https://ifconfig.co) for example.

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
| Jellyseerr           | `<IP>:8004`  |
| Radarr               | `<IP>:8010`  |
| Sonarr               | `<IP>:8011`  |
| Removarr             | `<IP>:8012`  |

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
### Transmission

Nothing to setup or maybe the "Speed Limits" depending on your internet connection.

### Jackett

Check the box:

- External access
- Cache enabled (recommended)

Add these values:

- "Cache TTL (seconds):" `2100`
- "Cache max results per indexer:" `1000`
- "FlareSolverr API URL:" `http://10.10.66.100:8191`    # **if you don't change anything on the docker-compose, that's it**
- "FlareSolverr Max Timeout (ms):" `100000`

Leave the rest blank.

Add your indexer(s).

### Radarr & Sonarr

Follow these [guides](https://trash-guides.info/).

This is a config to prefer download WEB-DL 1080p x264 *NOT 10bit* files.

#### Radarr Settings

Format: `Name: X|req|neg ; regex`

> Name: name of the condition

> X: neither "Negate" nor "Required" checked

> regex: Regular Expression

If there is **something** before the condition, it means that when you clicked "import", you should choose the **something** instead of **Release title**.

1. Media Management:
    - check `Replace Illegal Characters`
    - Colon Replacement: `Delete`
    - Path /downloads/medias/movies
2. Profiles
    - ![Profiles](radarr-profiles.png)
3. Quality: Not changed
4. Custom Formats: global
    1. 10bit: req ; `\b10bit\b`
    2. 3D:
        1. 3D: X ; `\b3d|sbs|half[ .-]ou|half[ .-]sbs\b`
        2. BluRay3D: X ; `\b(BluRay3D)\b`
    5. x265 (HD):
        1. x265/HEVC: req ; `[xh][ ._-]?265|\bHEVC(\b|\d)`
        2. **Resolution** Not 2160p: reg+neg ; `R2160p`
    7. HDR-10-10+:
        1. HDR10+: req ; `\bHDR10(\+|P(lus)?\b)`
        2. HDR10: req ; `\bHDR10(\b[^+|Plus])`
        3. Not DV HDR10: neg+req ; `^(?=.*\b(DV|DoVi|Dolby[ .]?Vision)\b)(?=.*\b(HDR(10)?(?!\+))\b)`
        4. HDR: req ; `\b(HDR)\b`
        5. Not DV ; neg+req ; `\b(dv|dovi|dolby[ .]?vision)\b`
        6. Not PQ: neg+req ; `\b(PQ)\b`
        7. Not HLG: neg+req ; `\bHLG(\b|\d)`
        8. Not SDR: neg+req ; `\bSDR(\b|\d)`
        9. **Release Group** Not RlsGrp (Missing HDR): neg+req ; `\b(FraMeSToR|HQMUX|SiCFoI)\b`
4. Custom Formats: French settings
    1. French Audio:
        1. **Language** French Language: X ; `French`
        2. French Original Version: X ; `\bVOF\b`
        3. TRUEFRENCH: X ; `\b(TRUEFRENCH|VFF?)\b`
        4. French International: X ; `\bVF(I|\d)\b`
    5. Multi Audio:
        1. MULTi: X ; `\b(MULTi)(\d|\b)`
        2. VO and VF: X ; `^(?=.*\b(VO)\b)(?=.*\b(VF(F|I)?)\b)`
    6. Multi French:
        1. MULTi: req ; `\b(MULTi)(\b|\d)`
        2. **Language** Original Audio: req ; `Original`
        3. **Language** French Audio: req ; `French`
    7. VFF: req ; `\b(TRUEFRENCH|VFF)\b`
5. Indexer: Add Torznab ; on Jackett click on "Copy Torznab Feed" and paste it in "URL" and copy-paste the API key pf jackett in API ; check everything ; select the categories you want
6. Download Client:
    - add transmission
    - host: 10.10.66.100
    - port: 9091
    - set username and password
    - recent priority: `last`
    - older priority: `last`
    - check `Remove Completed`
    - `Remote Path Mappings`: Host: `10.10.66.100 (Transmission)` ; Remote Path: `/data/completed` ; Local Path: `/data/completed`

#### Sonarr Settings

1. Media Management:
    - check `Replace Illegal Characters`
    - Path /downloads/medias/series
2. Profiles:
    - ![Quality Profiles](sonarr-profiles.png)
    - Language Profile: Multi: check English and French, and move them to the top of the list (English first, then French)
    - [Release Profiles](https://trash-guides.info/Sonarr/Sonarr-Release-Profile-RegEx/)
    - You can add `/\bHDR(\b|\d)/` and `10bit` at `-10000` to avoid HDR and 10bit releases
    - For Multi audio (VO+VFF):
        ```
        /\bMULTi(\b|\d)/i ; 10000
        /\bMULTi(\b|\d)/i ; 10000
        /\bVOF(\b|\d)/i   ; 8000
        /\b(TRUEFRENCH|VFF?)(\b|\d)/i ; 6000
        /\bFR(A|ENCH)?(\b|\d)/i ; 4000
        /\bFR(A|ENCH)?(\b|\d)/i ; 3000
        ```
    - The others settings are the same as in radarr.

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

Pay attention to not use CloudFlare tunnel for Jellyfin streaming, you may be banned for breaking [TOS](https://www.cloudflare.com/en-gb/terms/).

### Webhooks

I provide some webhooks for Jellyfin. These webhooks are used for:

- [Discord](#discord-webhook)
- [Microsoft Teams](#microsoft-teams-webhook)
- [WhatsApp (old-method)](#old-method-whatsapp-webhook)
- [WhatsApp (new-method)](#new-method-whatsapp-webhook)

First of all, you need to install the Jellyfin plugin called "Webhooks": Jellyfin > Dashboard > Plugins > Catalog > Webhook

Then, you need to restart Jellyfin:

```bash
$ cd /opt/chill/
$ docker-compose restart jellyfin
```

Now, go back to Jellyfin in the Plugins tab and click on Webhook.

The "*Server Url*" is your Jellyfin URL. If you expose it on internet, it's something like this: https://yourdomainname.com/jellyfin

*If you don't have a domain name, Jellyfin will not be able to display images (posters) in the Discord/Teams webhooks.*

#### Global Webhook

This method will allow you to send a webhook to any service/api you want in a very easy way.

This consists of using your own API and create your request in Python (which is more flexible than the Jellyfin Webhook plugin) and send it to the API you want.

To do this you will need to modify as your needs the [JellyHookAPI/jellyhookapi.py](https://github.com/garnajee/JellyHookAPI/blob/master/jellyhookapi.py) file.

Then, add the [Handlebars template](webhooks/jellyfin/global-item.handlebars) in Jellyfin > Plugin > Webhook > "Generic Destination".

And finally, build and run the docker image.

All these steps are explained in the [JellyHookAPI/README](https://github.com/garnajee/JellyHookAPI/tree/master#jellyhookapi) of the JellyHookAPI folder.

##### Discord Webhook

To add a **Discord** webhook:

- click on "Add Discord Destination"
- "*Webhook Name*": what you want
- "*Webhook Url*": the discord webhook url
- "*Notification type*": 
  1. if you want to receive notification when a new item (movie/tv show/...) is added, check "*Item Added*"
  2. or when a user is locked out (because of too much wrong password during connection), check "*User Locked Out*"
  3. or when a user is created/deleted, when a password is changed, ... (for every use case check [this file](webhooks/jellyfin/discord/discord-users.handlebars)), check "*Authentication \**" and "*User \**"
- "*User Filter*": personally, I don't check anything here
- "*Item Type*": check everything (depending on your webhook template) **except** "*Send All Properties*"
- "*Template*": (copy and paste the content)
  1. [webhooks/jellyfin/discord/discord-item.handlebars](webhooks/jellyfin/discord/discord-item.handlebars)
  2. [webhooks/jellyfin/discord/discord-users-locked-out.handlebars](webhooks/jellyfin/discord/discord-users-locked-out.handlebars)
  3. [webhooks/jellyfin/discord/discord-users.handlebars](webhooks/jellyfin/discord/discord-users.handlebars)
- "*Avatar Url*": just change the avatar profile picture directly on Discord
- "*Webhook Username*": should not be empty, but you can write what you want, the real username is defined directly in Discord
- "*Mention Type*": I never used this
- "*Embed Color*": color of the embedded message

Then click save.

##### Microsoft Teams Webhook

To add a **Microsoft Teams** webhook:

- click on "Add a Generic Destination"
- check the steps for Discord, it's the same
- "*Template*":
  1. "*Item Added*": [webhooks/jellyfin/ms-teams/teams-items.handlebars](webhooks/jellyfin/ms-teams/teams-items.handlebars)
  2. "*User Locked Out*": [webhooks/jellyfin/ms-teams/teams-users-locked-out.handlebars](webhooks/jellyfin/ms-teams/teams-users-locked-out.handlebars)
  3. "*User*": [webhooks/jellyfin/ms-teams/teams-users.handlebars](webhooks/jellyfin/ms-teams/teams-users.handlebars)
  
##### Old method WhatsApp Webhook

(***Old method - please refer to [the Global Webhook section](#global-webhook) for the new (and better) method.***)

To add a **WhatsApp** webhook:

Not as easy as the others.

You need to connect your WhatsApp account as if you were logging on WhatsApp Web.

To achieve this, you're going to use another docker-compose to self-host a WhatsApp HTTP API. I'm using [this API](https://github.com/devlikeapro/whatsapp-http-api).

Follow these steps:

```bash
$ cd /opt/chill
$ wget https://raw.githubusercontent.com/garnajee/home-server/master/docker-compose-whatsapp.yml
$ docker-compose --file docker-compose-whatsapp.yml up -d
```

> Note that the docker-compose I provided is not really optimized, you can add environment variable to better configure. You can check the documentation [here](https://waha.devlike.pro/docs/how-to/config/).

> Feel free to modify and perhaps make a pull request!

Then follow the [official](https://github.com/devlikeapro/whatsapp-http-api#3-start-a-new-session) from step **3** to **5**. For any further information, like the id of a contact or a group, please read the [documentation](https://waha.devlike.pro/docs/how-to/).

Go back to Jellyfin > Plugin > Webhook:

- click on "Add Generic Form Destination"
- "*Webhook Url*": the **internal** docker ip, if you don't change anything in the docker-compose it should be: `http://10.10.66.200:3000/api/sendText`
- then check what you want depending on the template

Then copy and paste the template you want:

1. "*Item Added*": [webhooks/jellyfin/whatsapp/whatsapp-items.handlebars](webhooks/jellyfin/whatsapp/whatsapp-items.handlebars)
2. (very basic) "*User created/deleted*": [webhooks/jellyfin/whatsapp/whatsapp-basic-user.handlebars](webhooks/jellyfin/whatsapp/whatsapp-basic-user.handlebars)

And finally you need to 2 Headers:

1. "*Key*": "accept", "*Value*": "application/json"
2. "*Key*": "Content-Type", "*Value*": "application/json"

> Please note, that we cannot send images with this API (it's a paid feature).

> (If you want to send the poster, refer to the new method [*(Global Webhook)*](#global-webhook).)

And that's it, you can save.

##### New method WhatsApp Webhook

***Please refer to the [whatsapp-api/README](whatsapp-api#whatsapp-api) to install and configure this API.***

This API allows you to send much more things than the previous one.

### Fake Ratio

If you need to fake your upload in order to have a ratio >= 1, you can use [Ratio.py](https://github.com/garnajee/Ratio.py).

I don't recommend using this indefinitely, please consider sharing to the community.

# License

This project is under [MIT](LICENSE) License.
