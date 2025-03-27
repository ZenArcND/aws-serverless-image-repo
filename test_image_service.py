import base64
import os

import boto3
import pytest

from microservices.config.image_service_config import (
    IMAGE_SRV__DYNAMODB_TABLE_NAME,
    IMAGE_SRV__REGION,
    IMAGE_SRV__S3_BUCKET_NAME,
)
from microservices.exceptions.custom_exceptions import ResourceNotFoundException
from microservices.service.image_service import (
    delete_image,
    get_image,
    upload_image,
)

# Set up LocalStack endpoints
LOCALSTACK_URL = os.getenv("LOCALSTACK_URL", "http://192.168.0.30:4566")

@pytest.fixture(scope="module")
def aws_localstack():

    s3 = boto3.client("s3", region_name=IMAGE_SRV__REGION, endpoint_url=LOCALSTACK_URL)
    dynamodb = boto3.resource("dynamodb", region_name=IMAGE_SRV__REGION, endpoint_url=LOCALSTACK_URL)

    # Create S3 bucket
    s3.create_bucket(Bucket=IMAGE_SRV__S3_BUCKET_NAME)

    # Create DynamoDB table
    table = dynamodb.create_table(
        TableName=IMAGE_SRV__DYNAMODB_TABLE_NAME,
        KeySchema=[{"AttributeName": "image_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "image_id", "AttributeType": "S"}]
    )
    
    yield s3, table

def test_upload_image(aws_localstack):
    s3, table = aws_localstack
    image_data = base64.b64encode(b"test image").decode("utf-8")
    image_metadata = {"filename": "test.jpg", "user_id": "123", "image_type": "jpeg"}

    response = upload_image(image_data, image_metadata)
    assert response["filename"] == "test.jpg"
    assert "s3_url" in response


def test_get_image_not_found(aws_localstack):
    with pytest.raises(ResourceNotFoundException):
        get_image("adfsdfsd")


def test_delete_image(aws_localstack):
    image_data = base64.b64encode(b"test data").decode("utf-8")
    image_metadata = {"filename": "test.jpg", "user_id": "123", "image_type": "jpeg"}

    image = upload_image(image_data, image_metadata)
    delete_image(image["image_id"])
    
    with pytest.raises(ResourceNotFoundException):
        get_image(image["image_id"])
