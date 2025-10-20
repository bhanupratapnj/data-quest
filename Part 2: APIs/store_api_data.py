import boto3
import requests

# ---------------------------------------------------------
# Configuration Section
# ---------------------------------------------------------

# Name of the target S3 bucket in your AWS account
S3_BUCKET_NAME = "rearc-dataquest-s3bucket"

# API endpoint providing national population data from DataUSA
DATA_SOURCE_URL = (
    "https://honolulu-api.datausa.io/tesseract/data.jsonrecords?"
    "cube=acs_yg_total_population_1&drilldowns=Year%2CNation&"
    "locale=en&measures=Population"
)

# ---------------------------------------------------------
# AWS S3 Initialization
# ---------------------------------------------------------

# Create an S3 service resource using boto3
# (This assumes your AWS credentials are properly configured in the environment)
s3_resource = boto3.resource('s3')

# Reference the specific bucket where data will be uploaded
target_bucket = s3_resource.Bucket(S3_BUCKET_NAME)

# ---------------------------------------------------------
# API Data Retrieval
# ---------------------------------------------------------

# Send an HTTP GET request to the API endpoint
# The response contains JSON-formatted population data
response = requests.get(DATA_SOURCE_URL)

# Extract the text content (raw JSON string) from the API response
api_response_text = response.text

# Print response information for debugging and verification
print("HTTP Response Object:", response)
print("Response Data Preview:", api_response_text[:500])  # Print first 500 chars for readability

# ---------------------------------------------------------
# Upload Data to AWS S3
# ---------------------------------------------------------

# Upload the retrieved API data as a JSON file to the specified S3 bucket
# - Key defines the filename (path) within the bucket
# - Body is the file content (the API JSON response)
target_bucket.put_object(
    Key="nation_population.json",  # File name in the S3 bucket
    Body=api_response_text         # File content (raw JSON data)
)

print("Data successfully uploaded to S3 bucket:", S3_BUCKET_NAME)
