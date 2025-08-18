PROJECT_ID=just-ratio-467615-s1
REGION=northamerica-northeast2
REPO_NAME=default
IMAGE_PATH="gcr.io/just-ratio-467615-s1/friendly-cicd-helper:latest"
gcloud config set project $PROJECT_ID
gcloud builds submit . --substitutions "_IMAGE_PATH=$IMAGE_PATH"
gcloud builds submit --config ./docs/demo-pipeline/print-cli-help.yaml --substitutions "_IMAGE_PATH=$IMAGE_PATH"