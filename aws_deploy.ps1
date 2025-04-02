Set-ExecutionPolicy Unrestricted -Scope Process

$env:AWS_ACCESS_KEY_ID="test"
$env:AWS_DEFAULT_REGION="us-east-1"
$env:AWS_SECRET_ACCESS_KEY="test"
$env:AWS_ENDPOINT="http://192.168.0.30:4566"

$CODE_UPLOAD_BUCKET_NAME="lambda-function-source"
$CODE_UPLOAD_BUCKET_REGION="us-east-1"
$AWS_ENDPOINT="http://192.168.0.30:4566"
$LAMBDA_ZIP_NAME="lamba-function.zip"
$CLOUD_FORMATION_TEMPLATE_FILE="cf-template.yaml"

# Zip the Lambda Archive
Compress-Archive -path microservices -DestinationPath $LAMBDA_ZIP_NAME -Force
aws --endpoint-url=$AWS_ENDPOINT s3api create-bucket --bucket $CODE_UPLOAD_BUCKET_NAME --region $CODE_UPLOAD_BUCKET_REGION 2>$null

aws --endpoint-url=$AWS_ENDPOINT s3 cp $LAMBDA_ZIP_NAME "s3://$CODE_UPLOAD_BUCKET_NAME"


aws --endpoint-url=$AWS_ENDPOINT cloudformation deploy --stack-name montycloud-image-service --template-file $CLOUD_FORMATION_TEMPLATE_FILE