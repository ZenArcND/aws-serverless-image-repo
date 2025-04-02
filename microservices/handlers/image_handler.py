import os
import sys
package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "package"))
sys.path.append(package_path)

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import ApiGatewayResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

from microservices.exceptions.custom_exceptions import ApiException
from microservices.service import image_service

Logger = Logger()

app = ApiGatewayResolver()

#---------------------
#  POST /image -> Uploading a new image
#---------------------
@app.post("/image")
def upload_image():
    image_req_data = app.current_event.json_body

    image_base64_data = image_req_data.get("image_data")
    image_metadata = image_req_data.get("image_metadata")

    res = image_service.upload_image(image_base64_data, image_metadata)
    return res, 201

#---------------------
#  GET /image/<image_id> -> Get Image Metadata
#---------------------
@app.get("/image/<image_id>")
def get_image(image_id: str):
    return image_service.get_image(image_id)


#---------------------
#  DELETE /image/<image_id> -> Delete Image from Reporsitory
#---------------------
@app.delete("/image/<image_id>")
def delete_image(image_id: str):
    image_service.delete_image(image_id)
    return {"status": "Success"}, 200


#---------------------
#  POST /images -> List all image from repo with filters user_id and image_type
#---------------------
@app.post("/images")
def list_images():
    image_req_data = app.current_event.json_body

    request_filters = image_req_data.get("filters", None)
    if not request_filters:
        return image_service.list_images()
    
    user_filter = request_filters.get("user_id", None)
    image_type_filter = request_filters.get("image_type", None)

    return image_service.list_images(user_filter, image_type_filter)


#---------------------
#  Common Exception Handler
#---------------------
# @app.exception_handler(Exception)
# def handle_exception(ex):
#     if isinstance(ex, ApiException):
#         return ex.get_response()
#     else:
#         return ApiException("Unknown Error", 500).get_response()



# ----------Lambda Entry Point---------
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)