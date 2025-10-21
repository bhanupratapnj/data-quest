import json
import pandas as pd
import requests
import boto3
import os

def lambda_handler(event, context):

    # Data Source 
    BLS_PRODUCTIVITY_URL = "https://rearc-dataquest-s3bucket.s3.amazonaws.com/pr.data.0.Current"
    US_POPULATION_URL = "https://rearc-dataquest-s3bucket.s3.amazonaws.com/nation_population.json"

    # Load Productivity Data
    bls_productivity_df = pd.read_csv(BLS_PRODUCTIVITY_URL, delimiter="\t")

    # Load Population Data (JSON)
    response = requests.get(US_POPULATION_URL)
    population_json = response.json()
    us_population_df = pd.json_normalize(population_json, record_path="data")

    # Filter Population Data (2013–2018) 
    us_population_df["Year"] = us_population_df["Year"].astype(int)
    filtered_population_df = us_population_df[
        (us_population_df["Year"] >= 2013) & (us_population_df["Year"] <= 2018)
    ]

    # Compute Statistics
    average_population = filtered_population_df["Population"].mean()
    population_std_dev = filtered_population_df["Population"].std()

    # Clean Productivity Data
    bls_productivity_df.rename(columns={
        "series_id        ": "series_id",
        "       value": "value"
    }, inplace=True)

    # Summarize Productivity Data
    series_yearly_summary_df = (
        bls_productivity_df
        .groupby(["series_id", "year"], as_index=False)["value"]
        .agg("sum")
    )

    max_value_per_series_df = (
        series_yearly_summary_df
        .sort_values("value", ascending=False)
        .drop_duplicates(subset="series_id", keep="first")
        .sort_index()
        .reset_index(drop=True)
    )

    # Filter Productivity Series for PRS30006032 & Q01
    filtered_productivity_series_df = bls_productivity_df[
        bls_productivity_df["series_id"].str.contains("PRS30006032", case=False)
    ]
    filtered_productivity_series_df = filtered_productivity_series_df[
        filtered_productivity_series_df["period"].str.contains("Q01", case=False)
    ]

    # Prepare and Clean Population Data
    us_population_df["Population"] = us_population_df["Population"].astype(int)

    # Merge Productivity and Population
    merged_productivity_population_df = pd.merge(
        filtered_productivity_series_df,
        us_population_df,
        left_on="year",
        right_on="Year",
        how="left"
    )

    final_combined_df = merged_productivity_population_df[
        ["series_id", "year", "period", "value", "Population"]
    ]

    # Prepare the Final Result
    result = {
        "population_stats": {
            "average_population": round(average_population, 2),
            "std_dev": round(population_std_dev, 2)
        },
	"max_productivity_values": max_value_per_series_df.head(5).to_dict(orient="records"),
        "merged_data_sample": final_combined_df.head(5).to_dict(orient="records")
    }

    # Upload to S3 
    s3 = boto3.client("s3")
    bucket_name = os.environ.get("S3_BUCKET_NAME", "rearc-dataquest-s3terraform")
    s3.put_object(
        Bucket=bucket_name,
        Key="lambda_outputs/result.json",
        Body=json.dumps(result, indent=2),
        ContentType="application/json"
    )

    return {
        "statusCode": 200,
        "body": json.dumps(result, indent=2)
    }
