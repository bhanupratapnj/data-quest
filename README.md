# Data Quest
This is repository to create a data pipeline architecture utilizing AWS Cloud.

## <ins> Part 1: AWS S3 & Sourcing Datasets </ins>

### 1. Republish this open dataset in Amazon S3 and share with us a link.
###  <ins> Storage Links </ins>
#### <ins> Amazon S3 bucket </ins>
https://us-east-2.console.aws.amazon.com/s3/buckets/rearc-dataquest-s3bucket?region=us-east-2&bucketType=general
#### <ins> pr.class </ins>
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/pr.class
#### <ins> pr.contacts </ins> 
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/pr.contacts
#### <ins> pr.data.0.Current </ins> 
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/pr.data.0.Current
#### <ins> pr.data.1.AllData </ins> 
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/pr.data.1.AllData
#### <ins> pr.duration </ins> 
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/pr.duration
#### <ins> pr.footnote </ins> 
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/pr.footnote
#### <ins> pr.measure </ins> 
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/pr.measure
#### <ins> pr.seasonal </ins> 
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/pr.seasonal
#### <ins> pr.sector </ins> 
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/pr.sector
#### <ins> pr.class </ins>
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/pr.series
#### <ins> pr.txt </ins>
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/pr.txt


### 2. Script this process so the files in the S3 bucket are kept in sync with the source when data on the website is updated, added, or deleted
Refer Python script **sync_bls_data.py** available under Part1 folder.


## <ins> Part 2: APIs </ins>

### 1. Create a script that will fetch data from this API.
Refer Python script **get_api_data.py** available under Part2 folder.

### 2. Save the result of this API call as a JSON file in S3.
#### <ins> nation_population.json </ins>
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/pr.txt
https://rearc-dataquest-s3bucket.s3.us-east-2.amazonaws.com/nation_population.json


## <ins> Part 3: Data Analytics </ins>
Refer **data_analysis.ipynb** available under Part3 folder.


## <ins> Part 4: Infrastructure as Code & Data Pipeline with AWS CDK. </ins>
I decided to attempt Part4 using Terraform. Researched on Terraform and stuided the basic of Terraform. Followed below links:
https://developer.hashicorp.com/terraform/tutorials/aws-get-started/infrastructure-as-code

https://www.youtube.com/watch?v=wAwVOFf0Xq4 

## <ins> IaC using Terraform </ins>

<img width="1036" height="323" alt="image" src="https://github.com/user-attachments/assets/81507ce9-34fe-4d3e-b033-8afd226ded30" />

#### <ins> Terraform codes: </ins>
01-tf-s3.tf
01-tf-lambda-load.tf
01-tf-eventbridge-sqs.tf

#### <ins> Lambda codes are available in below files: </ins>
data_load.py
data_reporting.py



