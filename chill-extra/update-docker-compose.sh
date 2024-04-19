#!/usr/bin/env bash
# run as root

# get current vesion
CURRENT_VERSION=$(docker-compose --version|awk '{print $4}')
echo "Current version: ${CURRENT_VERSION}"

# get latest release tag
TAG=$(curl -s GET https://api.github.com/repos/docker/compose/tags\?per_page\=1| awk -F'[:,"]' '/"name"/{print $5}')
echo "Latest release: ${TAG}"

# if superior or equal to the new release
if [ "${CURRENT_VERSION}" \> "${TAG}" ] || [ "${CURRENT_VERSION}" = "${TAG}" ]; then
    echo "Current version is superior or equal to the latest github release."
    echo "Exiting."
    exit 0
fi

# download latest compose release
# for linux-x86_64
ARCHI="linux-x86_64"

echo "Downloading for ${ARCHI}"
echo
CMD="curl -SL https://github.com/docker/compose/releases/download/${TAG}/docker-compose-${ARCHI} -o /usr/local/bin/docker-compose"

echo "${CMD}"

if eval ${CMD}; then
    echo "Docker-compose updated."
    echo $(docker-compose --version)
else
    echo "Error while downloading or replacing docker-compose."
fi

