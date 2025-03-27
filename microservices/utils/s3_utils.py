from urllib.parse import urlparse


def get_bucket_name(s3_url):

    # Assuming s3 url starts with s3://
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.netloc

    return bucket_name


def get_s3_object_path(s3_url):
    # Assuming s3 url starts with s3://
    parsed_url = urlparse(s3_url)
    object_key = parsed_url.path.lstrip('/')

    return object_key