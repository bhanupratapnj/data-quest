import boto3
import requests
from bs4 import BeautifulSoup
import os
import json

def lambda_handler(event, context):
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "rearc-dataquest-s3terraform")
    BLS_SOURCE_URL = "https://download.bls.gov/pub/time.series/pr/"
    DATA_SOURCE_URL = (
        "https://honolulu-api.datausa.io/tesseract/data.jsonrecords?"
        "cube=acs_yg_total_population_1&drilldowns=Year%2CNation&"
        "locale=en&measures=Population"
    )
    REQUEST_HEADERS = {
        "User-Agent": "project/1.0 (bhanu.tcs@gmail.com)"
    }

    # Initialize S3 resource
    s3_resource = boto3.resource("s3")
    s3_bucket = s3_resource.Bucket(S3_BUCKET_NAME)

    # Sync BLS data files
    existing_s3_files = [obj.key for obj in s3_bucket.objects.all()]
    potentially_deleted_files = existing_s3_files.copy()

    try:
        response = requests.get(BLS_SOURCE_URL, headers=REQUEST_HEADERS, timeout=30)
        response.raise_for_status()
        print(f"BLS directory response status: {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to retrieve BLS directory listing: {e}")
        return {"statusCode": 500, "body": json.dumps("Failed to retrieve BLS data.")}

    soup = BeautifulSoup(response.text, "html.parser")

    for link_tag in soup.find_all("a"):
        file_name = link_tag.get_text().strip()

        if not file_name or file_name == "[To Parent Directory]":
            continue

        file_url = BLS_SOURCE_URL + file_name

        try:
            file_response = requests.get(file_url, headers=REQUEST_HEADERS)
            file_response.raise_for_status()
        except requests.RequestException as error:
            print(f"Failed to download {file_name}: {error}")
            continue

        if file_name not in existing_s3_files:
            print(f"Uploading new file: {file_name}")
            s3_bucket.put_object(Key=file_name, Body=file_response.content)
        else:
            s3_object = s3_bucket.Object(file_name).get()
            existing_file_content = s3_object["Body"].read()
            if file_response.content != existing_file_content:
                print(f"Updating modified file: {file_name}")
                s3_bucket.put_object(Key=file_name, Body=file_response.content)
            potentially_deleted_files.remove(file_name)

    # Delete obsolete files (except JSON output)
    for file_name in potentially_deleted_files:
        if file_name != "nation_population.json":
            print(f"Deleting obsolete file: {file_name}")
            s3_bucket.Object(file_name).delete()

    print("BLS sync complete.")

    # Fetch API data
    try:
        api_response = requests.get(DATA_SOURCE_URL, timeout=30)
        api_response.raise_for_status()
        api_data = api_response.text
        print(f"API fetch success (status {api_response.status_code})")
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to fetch API data"})
        }

    try:
        s3_bucket.put_object(
            Key="nation_population.json",
            Body=api_data,
            ContentType="application/json"
        )
        print(f"Population data uploaded to S3 bucket: {S3_BUCKET_NAME}")
    except Exception as e:
        print(f"Error uploading API data to S3: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to upload API data to S3"})
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "BLS sync and api upload completed successfully.",
            "s3_bucket": S3_BUCKET_NAME,
            "bls_files_checked": len(existing_s3_files),
            "bls_files_deleted": len(potentially_deleted_files),
            "datausa_api_status": api_response.status_code,
            "population_file_key": "nation_population.json"
        })
    }
