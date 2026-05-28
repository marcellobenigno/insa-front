#!/usr/bin/env bash
set -euo pipefail

REMOTE_HOST="ubuntu@geoserver.multisig.com.br"
REMOTE_DEST="/home/ubuntu"
REMOTE_TILES_DIR="/var/lib/tomcat9/webapps/tiles"
TILES_DIR="$(cd "$(dirname "$0")/../public/tiles" && pwd)"
ARCHIVE="insa_layers.tar.gz"

echo "==> Compactando tiles..."
cd "$TILES_DIR"
COPYFILE_DISABLE=1 tar -zcf "$ARCHIVE" insa_layers
echo "    Arquivo: $TILES_DIR/$ARCHIVE ($(du -sh "$ARCHIVE" | cut -f1))"

echo "==> Enviando para $REMOTE_HOST..."
scp "$ARCHIVE" "$REMOTE_HOST:$REMOTE_DEST/"

echo "==> Extraindo no servidor..."
ssh "$REMOTE_HOST" bash <<EOF
  set -euo pipefail
  cd "$REMOTE_TILES_DIR"
  sudo mv "$REMOTE_DEST/$ARCHIVE" .
  sudo rm -rf insa_layers
  sudo tar -zxf "$ARCHIVE"
  sudo rm "$ARCHIVE"
  echo "    Tiles em: $REMOTE_TILES_DIR/insa_layers"
EOF

echo "==> Limpando arquivo local..."
rm "$TILES_DIR/$ARCHIVE"

echo ""
echo "Deploy concluído."
