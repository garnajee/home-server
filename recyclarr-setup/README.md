# Recyclarr

[Recyclarr](https://github.com/recyclarr/recyclarr) will help you to automate the configuring Radarr/Sonarr qualities.

You'll find here the following instructions to be able to download files in that specific quality:

- `MULTi` (Original version + Truefrench (in my case))
- `1080p`
- `h264`
- and **no** `HDR` or `10 bits` (for the last one, refer to the [custom script part](#custom-script))

For more detailed instructions and additional configurations, please refer to the [Recyclarr wiki](https://recyclarr.dev/wiki/).

## Table of Contents

1. [Installation](#installation)
2. [Setup](#setup)
   - [First-time Launch of Recyclarr](#first-time-launch-of-recyclarr)
   - [Downloading Configuration Files](#downloading-configuration-files)
   - [Second Launch](#second-launch)
3. [Additional Configuration](#additional-configuration)
4. [Import Your Custom Profile](#custom-script)

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
4. Download the provided `.env-example` file (the command renamed it to `.env`). Modify the `.env` file according to your environment:
   ```bash
   curl -o .env https://raw.githubusercontent.com/garnajee/home-server/master/recyclarr-setup/.env-example
   ```

## Setup

Throughout the process you must be in the `recyclarr` folder

### First-time Launch of Recyclarr

Run the following command to initialize Recyclarr:
```bash
docker-compose run --rm recyclarr config create
```

This will also create a starter configuration file (`config/recyclarr.yml`), but we won't use this one.

### Downloading Configuration Files

After launching the first-time setup, download my predefined Radarr and Sonarr configuration files:
```bash
curl -o config/configs/radarr.yml https://raw.githubusercontent.com/garnajee/home-server/master/recyclarr-setup/radarr.yml
curl -o config/configs/sonarr.yml https://raw.githubusercontent.com/garnajee/home-server/master/recyclarr-setup/sonarr.yml
```

### Second Launch

Modify the configuration of `radarr.yml` and `sonarr.yml` (located in `config/config/`) and especially the `base_url` and `api_key` fields.

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

After setting up the Recyclarr configurations, there are a few additional configurations you need to do:

### Change The Quality Profile Language in Radarr/Sonarr

1. Open your Radarr or Sonarr web interface.
2. Navigate to Settings > Profiles.
3. Click on your newly created profile ("Any")
3. Locate the "Language" option and set it to "Any" to ensure maximum compatibility

### Remove Default Profile in Radarr/Sonarr

1. In your Radarr or Sonarr web interface, go to Settings > Profiles.
2. Find the default profile and remove it, as it may conflict with Recyclarr's custom profiles imported.

---

# Custom Script

I created a Python script for importing custom formats.

If you have specific requirements, you can use my script to import your custom format into Radarr/Sonarr. You'll have to modify the "`json_file_path`" value in the script.

In order to use the `import-cf.py` script, follow these steps:

- install the `requests` lib: `pip install requests`
- download the script and custom format:
```bash
curl -O https://raw.githubusercontent.com/garnajee/home-server/master/recyclarr-setup/10bits.json 
curl -O https://raw.githubusercontent.com/garnajee/home-server/master/recyclarr-setup/import-cf.py
```
- modify the script: Change the value of `base_url` and `api_key` with your Radarr/Sonarr corresponding values.
- run the script: `python3 impor-cf.py`

