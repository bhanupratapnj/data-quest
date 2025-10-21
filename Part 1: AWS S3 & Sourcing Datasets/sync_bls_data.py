import boto3
import requests
from bs4 import BeautifulSoup

# Define AWS S3 bucket
S3_BUCKET_NAME = "rearc-dataquest-s3bucket"

# Define source URL for BLS data files
BLS_SOURCE_URL = "https://download.bls.gov/pub/time.series/pr/"

# Define request headers along with a valid User-Agent
REQUEST_HEADERS = {
    "User-Agent": "project/1.0 (bhanu.tcs@gmail.com)"
}

# Initialize S3 resource 
s3_resource = boto3.resource('s3')
s3_bucket = s3_resource.Bucket(S3_BUCKET_NAME)

# Retrieve list of all existing file names in the S3 bucket
existing_s3_files = [obj.key for obj in s3_bucket.objects.all()]
print("Existing files in S3 bucket:")
print(existing_s3_files)

# Make a copy of the existing S3 file list to track files that should be deleted later
potentially_deleted_files = existing_s3_files.copy()

# Send HTTP GET request to BLS with headers
response = requests.get(BLS_SOURCE_URL, headers=REQUEST_HEADERS)
print(f"BLS directory response status: {response.status_code}")

# Parse the HTML directory listing with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Iterate through all the files listed on BLS 
for link_tag in soup.find_all("a"):
    file_name = link_tag.get_text()

    # Skip the parent directory link
    if file_name == "[To Parent Directory]":
        continue

    file_url = BLS_SOURCE_URL + file_name

    # Download the file from the BLS site
    try:
        file_response = requests.get(file_url)
        file_response.raise_for_status()  # Raises an error for bad HTTP codes
    except requests.RequestException as error:
        print(f"Failed to download {file_name}: {error}")
        continue

    # --- Upload New Files ---
    if file_name not in existing_s3_files:
        print(f"Uploading new file: {file_name}")
        s3_bucket.put_object(Key=file_name, Body=file_response.content)

    # --- Update Existing Files ---
    else:
        # Retrieve the existing file from S3
        s3_object = s3_bucket.Object(file_name).get()
        existing_file_content = s3_object['Body'].read()

        # Compare contents of S3 and BLS versions
        if file_response.content != existing_file_content:
            print(f"Updating modified file: {file_name}")
            s3_bucket.put_object(Key=file_name, Body=file_response.content)

        # Remove the file from the "to be deleted" list since it's still active
        potentially_deleted_files.remove(file_name)

# Delete files from S3 that no longer exist on the BLS website.
# Do not delete "nation_population.json" as this is created in another script.
for file_name in potentially_deleted_files:
    if file_name != "nation_population.json":
        print(f"🗑️ Deleting obsolete file: {file_name}")
        s3_bucket.Object(file_name).delete()

print("Sync complete.")



