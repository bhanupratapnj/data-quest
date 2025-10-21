import boto3
import requests

# Name of the target S3 bucket 
S3_BUCKET_NAME = "rearc-dataquest-s3bucket"

# API endpoint 
DATA_SOURCE_URL = (
    "https://honolulu-api.datausa.io/tesseract/data.jsonrecords?"
    "cube=acs_yg_total_population_1&drilldowns=Year%2CNation&"
    "locale=en&measures=Population"
)

# Create S3 service resource
s3_resource = boto3.resource('s3')

# Bucket where data will be uploaded
target_bucket = s3_resource.Bucket(S3_BUCKET_NAME)

# Send an HTTP GET request to the API endpoint
response = requests.get(DATA_SOURCE_URL)

# Extract the text content from the API response
api_response_text = response.text

# Print response information for debugging and verification
print("HTTP Response Object:", response)
print("Response Data Preview:", api_response_text[:500])  # Print first 500 chars for readability

# Upload the retrieved API data as a JSON file to the specified S3 bucket
target_bucket.put_object(
    Key="nation_population.json",  # File name in the S3 bucket
    Body=api_response_text         # File content 
)

print("Data successfully uploaded to S3 bucket:", S3_BUCKET_NAME)
