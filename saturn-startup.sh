#/bin/bash
set -x
cd untitled1-vector-search/ && pwd

# ***
echo "Building FRONTEND..."
cd frontend/ && pwd

# install node (https://techviewleo.com/how-to-install-node-js-18-lts-on-ubuntu/)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install nodejs
npm install --global yarn
node --version
npm --version
yarn --version

export NODE_PATH=$(pwd)/frontend/node_modules
export PATH=$PATH:$(pwd)/frontend/node_modules/.bin

yarn install --no-optional
yarn build
cd ../

# ***
echo "Building BACKEND..."
cd backend/ && pwd

rm -rf vecsim_app/templates/
mkdir vecsim_app/templates
cp -r ../frontend/build vecsim_app/templates/build


python --version
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
pip install -e .


# ***
echo "Downloading MODELS..."
cd ../.. && pwd

curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-408.0.1-linux-x86_64.tar.gz
tar -xf google-cloud-cli-408.0.1-linux-x86_64.tar.gz
chmod +x ./google-cloud-sdk/install.sh
yes | ./google-cloud-sdk/install.sh
export PATH=$PATH:$(pwd)/google-cloud-sdk/bin/

cd untitled1-vector-search/ && pwd
export BUCKET_URI="gs://untitled1-vector-search/master"
for path in data/multilabel_classifier/checkpoint/ data/embeddings/; do
    mkdir -p $path
    time gsutil -m rsync -r $BUCKET_URI/$path $path
done
