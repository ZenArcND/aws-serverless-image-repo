import base64
import os

import boto3
import pytest

from microservices.config.image_service_config import (
    IMAGE_SRV__DYNAMODB_TABLE_NAME,
    IMAGE_SRV__REGION,
    IMAGE_SRV__S3_BUCKET_NAME,
    IMAGE_SRV__DYNAMODB_GSI__USERID,
    IMAGE_SRV__DYNAMODB_GSI__IMAGE_TYPE
)
from microservices.exceptions.custom_exceptions import ResourceNotFoundException
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from microservices.service.image_service import (
    delete_image,
    get_image,
    upload_image,
    list_images
)


@pytest.fixture(scope="module")
@pytest.mark.filterwarnings("error")
def aws_localstack():

    # try:
    #     s3 = boto3.client("s3", region_name=IMAGE_SRV__REGION, endpoint_url=os.getenv('AWS_ENDPOINT'))
    #     dynamodb = boto3.resource("dynamodb", region_name=IMAGE_SRV__REGION, endpoint_url=os.getenv('AWS_ENDPOINT'))

    #     # Create S3 bucket
    #     s3.create_bucket(Bucket=IMAGE_SRV__S3_BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': IMAGE_SRV__REGION})

    #     # Create DynamoDB table
    #     table = dynamodb.create_table(
    #         TableName=IMAGE_SRV__DYNAMODB_TABLE_NAME,
    #         KeySchema=[{"AttributeName": "image_id", "KeyType": "HASH"}],
    #         AttributeDefinitions=[
    #             {"AttributeName": "image_id", "AttributeType": "S"},
    #             {"AttributeName": "user_id", "AttributeType": "S"},
    #             {"AttributeName": "image_type", "AttributeType": "S"},
    #         ],
    #         BillingMode = "PAY_PER_REQUEST",
    #         GlobalSecondaryIndexes=[
    #             {
    #                 "IndexName": IMAGE_SRV__DYNAMODB_GSI__USERID,
    #                 "KeySchema": [
    #                     {"AttributeName": "user_id", "KeyType": "HASH"},
    #                     {"AttributeName": "image_type", "KeyType": "RANGE"},
    #                 ],
    #                 'Projection': {'ProjectionType': 'ALL'},
    #             },
    #             {
    #                 "IndexName": IMAGE_SRV__DYNAMODB_GSI__IMAGE_TYPE,
    #                 "KeySchema": [
    #                     {"AttributeName": "image_type", "KeyType": "HASH"},
    #                     {"AttributeName": "user_id", "KeyType": "RANGE"},
    #                 ],
    #                 'Projection': {'ProjectionType': 'ALL'},
    #             }
    #         ]
    #     )
        
    #     yield s3, table

    # finally:
    #     # Cleanup: delete S3 bucket and DynamoDB table
    #     try:
    #         # Empty and delete the S3 bucket
    #         objects = s3.list_objects_v2(Bucket=IMAGE_SRV__S3_BUCKET_NAME)
    #         if "Contents" in objects:
    #             s3.delete_objects(
    #                 Bucket=IMAGE_SRV__S3_BUCKET_NAME,
    #                 Delete={"Objects": [{"Key": obj["Key"]} for obj in objects["Contents"]]}
    #             )
    #         s3.delete_bucket(Bucket=IMAGE_SRV__S3_BUCKET_NAME)

    #         # Delete DynamoDB table
    #         table.delete()

    #     except Exception as e:
    #         print(f"Cleanup error: {e}")

    return None, None



def test_upload_image(aws_localstack):
    s3, table = aws_localstack
    image_data = base64.b64encode(b"test image").decode("utf-8")
    image_metadata = {"filename": "test.jpg", "user_id": "123", "image_type": "jpeg"}
    response = upload_image(image_data, image_metadata)

    image_id = response["image_id"]
    response = get_image(image_id)

    print(response)
    
    assert response["filename"] == "test.jpg"
    assert response["image_type"] == "jpeg"
    assert "s3_url" in response
    assert "image_id" in response


def test_get_image_not_found(aws_localstack):
    with pytest.raises(NotFoundError):
        get_image("adfsdfsd")


def test_delete_image(aws_localstack):
    image_data = base64.b64encode(b"test data").decode("utf-8")
    image_metadata = {"filename": "test.jpg", "user_id": "123", "image_type": "jpeg"}

    image = upload_image(image_data, image_metadata)
    delete_image(image["image_id"])
    
    with pytest.raises(NotFoundError):
        get_image(image["image_id"])



def test_image_list(aws_localstack):

    image_list_resp = list_images(user_id=2)
    assert image_list_resp == []

    image_data = base64.b64encode(b"test data").decode("utf-8")

    image_metadata10 = {"filename": "test10.jpg", "user_id": "1", "image_type": "jpeg"}
    upload_image(image_data, image_metadata10)
    image_metadata11 = {"filename": "test11.jpg", "user_id": "1", "image_type": "jpeg"}
    upload_image(image_data, image_metadata11)
    image_metadata12 = {"filename": "test12.png", "user_id": "1", "image_type": "png"}
    upload_image(image_data, image_metadata12)

    image_metadata20 = {"filename": "test20.jpg", "user_id": "2", "image_type": "jpeg"}
    upload_image(image_data, image_metadata20)
    image_metadata21 = {"filename": "test21.jpg", "user_id": "2", "image_type": "jpeg"}
    upload_image(image_data, image_metadata21)
    image_metadata22 = {"filename": "test22.jpg", "user_id": "2", "image_type": "jpeg"}
    upload_image(image_data, image_metadata22)

    image_list_resp = list_images(user_id="1")
    print(image_list_resp)
    assert len(image_list_resp) == 3
    for item in image_list_resp:
        assert item["user_id"] == "1"
        assert item["filename"] in ["test10.jpg", "test11.jpg", "test12.png"]

    image_list_resp = list_images(user_id="2", image_type="jpeg")
    assert len(image_list_resp) == 3
    for item in image_list_resp:
        assert item["user_id"] == "2"
        assert item["filename"] in ["test20.jpg", "test21.jpg", "test22.jpg"]

    image_list_resp = list_images(user_id="1", image_type="png")
    assert len(image_list_resp) == 1
    for item in image_list_resp:
        assert item["user_id"] == "1"
        assert item["filename"] in ["test12.png"]
