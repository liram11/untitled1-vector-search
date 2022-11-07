#!/bin/bash
cd "$(dirname "$0")"  # cd to the script's directory

git clone --branch dev2 git@github.com:liram11/untitled1-vector-search.git
cd untitled1-vector-search/ && pwd

## FRONTEND

# install node (https://techviewleo.com/how-to-install-node-js-18-lts-on-ubuntu/)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install nodejs
npm install --global yarn
node --version
npm --version
yarn --version

cd frontend/ && pwd
export NODE_PATH=$(pwd)/frontend/node_modules
export PATH=$PATH:$(pwd)/frontend/node_modules/.bin

yarn install --no-optional
yarn build


## BACKEND

cd ../backend/ && pwd

mkdir ./vecsim_app/templates/
cp -r ../frontend/build ./vecsim_app/templates/build


python --version
export PYTHONUNBUFFERED 1
export PYTHONDONTWRITEBYTECODE 1


# DATA, MODELS

curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-408.0.1-linux-x86_64.tar.gz
tar -xf google-cloud-cli-408.0.1-linux-x86_64.tar.gz
chmod +x ./google-cloud-sdk/install.sh
yes | ./google-cloud-sdk/install.sh
export PATH=$PATH:$(pwd)/google-cloud-sdk/bin/

BUCKET_URI="gs://untitled1-vector-search/master"

gsutil -m rsync -r $BUCKET_URI/data/multilabel_classifier/checkpoint/ data/multilabel_classifier/checkpoint/
gsutil -m rsync -r $BUCKET_URI/data/embeddings/ data/embeddings/


# Entrypoint

cd backend/vecsim_app
sh ./entrypoint.sh
