PROJECT_ID=just-ratio-467615-s1
REGION=northamerica-northeast2
REPO_NAME=default
IMAGE_PATH="gcr.io/just-ratio-467615-s1/friendly-cicd-helper:latest"
./google-cloud-sdk/bin/gcloud config set project $PROJECT_ID
./google-cloud-sdk/bin/gcloud builds submit . --substitutions "_IMAGE_PATH=$IMAGE_PATH"
./google-cloud-sdk/bin/gcloud builds submit --config ./docs/demo-pipeline/print-cli-help.yaml --substitutions "_IMAGE_PATH=$IMAGE_PATH"