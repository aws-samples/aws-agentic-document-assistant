import json
import boto3

# Initialize the S3 client
s3_client = boto3.client("s3")


def store_list_to_s3(bucket_name, object_key, data):
    # Serialize the list using json
    json_data = json.dumps(data)
    # Upload the json data to S3
    s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=json_data)


def load_list_from_s3(bucket_name, object_key):
    # Download the json data from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    json_data = response["Body"].read()

    data = json.loads(json_data)
    return data
