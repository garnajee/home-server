# Recyclarr

[Recyclarr](https://github.com/recyclarr/recyclarr) will help you to automate the configuring Radarr/Sonarr qualites.

You'll find here the following instructions to be able to download files in that specific quality:

- `MULTi` (Original version + Truefrench (in my case))
- `1080p`
- `h264`
- and **no** `HDR` or `10 bits`.

---
- installation
- setup temporaire
  - creation des dossiers
  - téléchargement du docker compose
    - rappel que le network DC doit etre dans le meme que celui de radarrr/sonarr
  - téléchargement des conf \*arr dans le bon emplacement
  - lancement de recyclarr pour la 1ere fois -> création de la config
  - 2e lancement
    - sync des profils radarr/sonarr v4
  - go sur radarr/sonarr : change langauge to "Any"
  - supprimer ancien profil (dafault one) sur radarr/sonarr
- ajout de custom profil spécifique non dispo dans les trashguides

---
---
---

# Guide to Installing, Configuring, and Using Recyclarr Docker

## Table of Contents

1. [Installation](#installation)
2. [Setup](#setup)
   - [First-time Launch of Recyclarr](#first-time-launch-of-recyclarr)
   - [Downloading Configuration Files](#downloading-configuration-files)
   - [Second Launch](#second-launch)
3. [Additional Configuration](#additional-configuration)

---

## Installation

To install Recyclarr, follow these steps:

1. Ensure you have Docker and Docker Compose installed on your system.
2. Create necessary directories and change directory to `recyclarr`:
   ```bash
   mkdir -p recyclarr/config
   cd recyclarr
   ```
3. Download the provided `docker-compose.yaml`:
   ```bash
   curl -O https://raw.githubusercontent.com/garnajee/home-server/master/recyclarr-setup/docker-compose.yaml
   ```

   > [!WARNING]
   > This docker-compose is associated with the `net-chill` docker subnet. Recyclarr needs to be on the same subnet as radarr and sonarr.
4. Download the provided `.env-example` file and rename it to `.env`. Modify the `.env` file according to your environment:
   ```bash
   curl -o .env https://raw.githubusercontent.com/garnajee/home-server/master/recyclarr-setup/.env-example
   ```

## Setup

Throughout the process you must be in `recyclarr` folder

### First-time Launch of Recyclarr

Run the following command to initialize Recyclarr and create a starter configuration file:
```bash
docker-compose run --rm recyclarr config create
```

### Downloading Configuration Files

After launching the first-time setup, download the Radarr and Sonarr configuration files:
```bash
curl -o config/radarr.yml https://raw.githubusercontent.com/garnajee/home-server/master/recyclarr-setup/radarr.yml
curl -o config/sonarr.yml https://raw.githubusercontent.com/garnajee/home-server/master/recyclarr-setup/sonarr.yml
```

### Second Launch

Modify the configuration of `radarr.yml` and `sonarr.yml` and especially the `base_url` and `api_key` fields.

Then, launch Recyclarr again:
```bash
docker-compose up -d
```
Then, enter the Recyclarr container shell:
```bash
docker-compose exec -it recyclarr bash
```

Inside the container shell, execute the following commands:

 - List local config files: `# recyclarr config list local`
 - Sync Radarr: `# recyclarr sync --config radarr.yml`
 - Sync Sonarr: `# recyclarr sync --config sonarr.yml`


## Additional Configuration



