Documentation of Image Repository Service

Modules:
---------
1. `microservices/handlers/image_handler.py` - API entry point, defines routes using AWS Lambda Powertools.
2. `microservices/service/image_service.py` - Business logic for handling images.
3. `microservices/utils/s3_utils.py` - Utility functions for parsing S3 URLs.
4. `microservices/exceptions/custom_exceptions.py` - Custom exception handling.
5. `microservices/config/image_service_config.py` - Configuration constants for S3 and DynamoDB.

API Endpoints:
--------------
1. **POST /image** - Upload a new image (Base64 encoded)
2. **GET /image/<image_id>** - Retrieve image metadata
3. **DELETE /image/<image_id>** - Delete an image
4. **POST /images** - List images with optional filters

API Request and Response:
-------------------------
