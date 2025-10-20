import boto3
import requests
from bs4 import BeautifulSoup

# --- Configuration Section ---
# Define your AWS S3 bucket name where the data will be synced
S3_BUCKET_NAME = "rearc-dataquest-s3bucket"

# Define the source URL where BLS (Bureau of Labor Statistics) data files are located
BLS_SOURCE_URL = "https://download.bls.gov/pub/time.series/pr/"

# Define request headers (BLS requires a valid User-Agent with contact info)
REQUEST_HEADERS = {
    "User-Agent": "project/1.0 (bhanu.tcs@gmail.com)"
}

# --- AWS S3 Initialization ---
# Initialize an S3 resource using boto3 and refer to the target bucket
s3_resource = boto3.resource('s3')
s3_bucket = s3_resource.Bucket(S3_BUCKET_NAME)

# --- Get Current Bucket Contents ---
# Retrieve a list of all existing object keys (file names) in the S3 bucket
existing_s3_files = [obj.key for obj in s3_bucket.objects.all()]
print("Existing files in S3 bucket:")
print(existing_s3_files)

# Make a copy of the existing S3 file list to track files that should be deleted later
# These are files that exist in S3 but are no longer available on the BLS site.
potentially_deleted_files = existing_s3_files.copy()

# --- Scrape the BLS Directory Page ---
# Send an HTTP GET request to the BLS data directory with headers
response = requests.get(BLS_SOURCE_URL, headers=REQUEST_HEADERS)
print(f"BLS directory response status: {response.status_code}")

# Parse the HTML directory listing with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# --- Synchronize Files Between BLS and S3 ---
# Iterate through all the hyperlinks (files) listed on the BLS data page
for link_tag in soup.find_all("a"):
    file_name = link_tag.get_text()

    # Skip the parent directory navigation link
    if file_name == "[To Parent Directory]":
        continue

    file_url = BLS_SOURCE_URL + file_name

    # Try to download the file from the BLS site
    try:
        file_response = requests.get(file_url)
        file_response.raise_for_status()  # Raises an error for bad HTTP codes
    except requests.RequestException as error:
        print(f"❌ Failed to download {file_name}: {error}")
        continue

    # --- Upload New Files ---
    if file_name not in existing_s3_files:
        print(f"⬆️ Uploading new file: {file_name}")
        s3_bucket.put_object(Key=file_name, Body=file_response.content)

    # --- Update Existing Files ---
    else:
        # Retrieve the existing file from S3
        s3_object = s3_bucket.Object(file_name).get()
        existing_file_content = s3_object['Body'].read()

        # Compare contents of S3 and BLS versions
        if file_response.content != existing_file_content:
            print(f"🔄 Updating modified file: {file_name}")
            s3_bucket.put_object(Key=file_name, Body=file_response.content)

        # Remove the file from the "to be deleted" list since it's still active
        potentially_deleted_files.remove(file_name)

# --- Remove Obsolete Files ---
# Delete files from S3 that no longer exist on the BLS website.
# The only exception is "nation_population.json", which should remain (created in another script).
for file_name in potentially_deleted_files:
    if file_name != "nation_population.json":
        print(f"🗑️ Deleting obsolete file: {file_name}")
        s3_bucket.Object(file_name).delete()

print("✅ Sync complete.")


