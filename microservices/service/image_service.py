import base64
import os
import uuid

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.exceptions import InternalServerError, NotFoundError

from microservices.config.image_service_config import (
    IMAGE_SRV__DYNAMODB_GSI__IMAGE_TYPE,
    IMAGE_SRV__DYNAMODB_GSI__USERID,
    IMAGE_SRV__DYNAMODB_TABLE_NAME,
    IMAGE_SRV__REGION,
    IMAGE_SRV__S3_BUCKET_NAME,
)
from microservices.exceptions.custom_exceptions import (
    ApiException,
    ResourceNotFoundException,
)
from microservices.utils import s3_utils

logger = Logger()


# Initialize the s3 client
__s3_client = boto3.client("s3", region_name = IMAGE_SRV__REGION, endpoint_url=os.getenv("AWS_ENDPOINT") )

# Initialize dynamo db client
__dynamodb_client = boto3.resource("dynamodb", region_name = IMAGE_SRV__REGION, endpoint_url=os.getenv("AWS_ENDPOINT"))
__dynamodb_image_table = __dynamodb_client.Table(IMAGE_SRV__DYNAMODB_TABLE_NAME)


#-----------------------------------------------------
# Service Functions
#------------------------------------------------------

#-----Service Function to Retrive Image Details--------

def get_image(image_id: str) -> dict:

    # Get Image Meta Data from Dynamo DB
    respose = __dynamodb_image_table.get_item(Key={"image_id": image_id})
    response_item = respose.get("Item", None)

    if not response_item:
        raise NotFoundError(f"Image with Key {image_id} not found")
    
    return response_item
    

# --------Service Function to upload new Image--------

def upload_image(image_data: str, image_metadata: dict) -> dict:

    try:
    
        # generate new image id
        image_id = str(uuid.uuid4())

        # convert base64 to bytes
        image_bytes = base64.b64decode(image_data)

        # upload to s3
        __s3_client.put_object(Bucket=IMAGE_SRV__S3_BUCKET_NAME, Key=image_id, Body=image_bytes, ContentType="image/jpeg")

        # construct the s3 url
        image_s3_url = f"s3://{IMAGE_SRV__S3_BUCKET_NAME}/{image_id}"

        # construct the metadata
        image_item = {
            "image_id": image_id, 
            "filename": image_metadata.get("filename"),
            "user_id": image_metadata.get("user_id"),
            "image_type": image_metadata.get("image_type"),
            "s3_url": image_s3_url
        }

        # Save item to Dynamo DB
        __dynamodb_image_table.put_item(Item=image_item)

        return image_item
    
    except Exception as e:
        logger.error(str(e))
        raise InternalServerError("Unable to save new Image. Internal Server Error")


# --------Service Function to delete existing Image--------

def delete_image(image_id: str) -> None:
    # Get the image meta data first
    
    img_meta_response = get_image(image_id)

    try:
        # Extract S3 URL
        image_s3_url = img_meta_response["s3_url"]
        s3_bucket_name = s3_utils.get_bucket_name(image_s3_url)
        s3_object_path = s3_utils.get_s3_object_path(image_s3_url)

        # Delete S3 Object
        __s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_object_path)

        # Delete Entry from Dynamo DB
        __dynamodb_image_table.delete_item(Key={"image_id": image_id})
    
    except Exception as e:
        logger.error(str(e))
        raise InternalServerError("Unable to delete image due to internal server error")


# --------Service Function to list Images--------

def list_images(user_id: str = None, image_type: str = None) -> list:

    try:

        scan_arguments = {}

        # Determine the GSI to scan
        if user_id and image_type:
            scan_arguments["IndexName"] = IMAGE_SRV__DYNAMODB_GSI__USERID
        elif user_id:
            scan_arguments["IndexName"] = IMAGE_SRV__DYNAMODB_GSI__USERID
        elif image_type:
            scan_arguments["IndexName"] = IMAGE_SRV__DYNAMODB_GSI__IMAGE_TYPE

        # Construct filter expressions
        filter_expression = []
        expression_values = {}

        # Check and build for user_id filter
        if user_id:
            filter_expression.append("user_id = :user_id")
            expression_values[":user_id"] = user_id

        # Check and build for user_type filter
        if image_type:
            filter_expression.append("image_type = :image_type")
            expression_values[":image_type"] = image_type

        # Apply filters if any
        if filter_expression:
            scan_arguments["FilterExpression"] = " AND ".join(filter_expression)
            scan_arguments["ExpressionAttributeValues"] = expression_values

        
        response = __dynamodb_image_table.scan(**scan_arguments)

        return response.get("Items",[])
    
    except Exception as e:
        logger.error(str(e))
        raise InternalServerError("Unable to list images. Internal Server Error")