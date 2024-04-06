#!/usr/bin/env bash

# Déplacer dans le dossier contenant le dossier whatsapp/
cd whatsapp || exit

# Récupérer le nom du dossier unique dans le répertoire whatsapp/
dossier_source=$(ls)

# Arrêter le docker-compose existant
echo "Arrêt du docker-compose existant..."
cd "$dossier_source" || exit
docker-compose down
cd ..

# Créer une sauvegarde compressée du dossier existant
echo "Création d'une sauvegarde du dossier existant..."
timestamp=$(date +"%d-%m-%Y--%H%M%S")
backup_file="../backup-not-used/whatsapp/backup_$timestamp.tar.gz"
tar -czf $backup_file $dossier_source

# Suppression de l'ancienne version
echo "Suppression de l'ancienne version..."
rm -rf $dossier_source

# Téléchargement de la dernière version depuis GitHub
echo "Téléchargement de la dernière version depuis GitHub..."
latest_release=$(curl -s https://api.github.com/repos/aldinokemal/go-whatsapp-web-multidevice/releases/latest | grep "tag_name" | awk -F '"' '{print $4}')
curl -LOk "https://github.com/aldinokemal/go-whatsapp-web-multidevice/archive/$latest_release.tar.gz"

# Extraction du fichier tar.gz
echo "Extraction du fichier tar.gz..."
tar -zxf $latest_release.tar.gz

# Suppression de l'archive
echo "Suppression de l'archive..."
rm -f $latest_release.tar.gz

# Récupérer le nom du dossier unique dans le répertoire
dossier_source=$(ls)

# Modification du fichier docker-compose.yml
echo "Modification du fichier docker-compose.yml..."
sed -i '/^\s*ports:$/,/^\s*$/d' $dossier_source/docker-compose.yml

cat <<EOT >> $dossier_source/docker-compose.yml
    ports:
      - "0.0.0.0:8888:3000"
    networks:
      net-chill:
        ipv4_address: 10.10.66.200

networks:
  net-chill:
    external: true
EOT

# Modification du fichier golang.Dockerfile
echo "Modification du fichier golang.Dockerfile..."
sed -i 's/ENTRYPOINT \["\/app\/whatsapp"\]/ENTRYPOINT \["\/app\/whatsapp", "-b=grumpily:RevivingPerplexedCider9Crept"\]/' $dossier_source/docker/golang.Dockerfile

echo "Modifications terminées !"

# Démarrage du docker-compose
cd $dossier_source || exit
echo "update de l'image docker..."
docker-compose pull
echo "démarrage du docker-compose..."
docker-compose up -d --build && docker-compose ps -a


echo "--> besoin de se reconnecter à whatsapp (<ip>:8888).
