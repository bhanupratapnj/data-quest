# Lambda function to load API data into S3
module "data_load" {
  source                 = "terraform-aws-modules/lambda/aws"
  version                = "8.1.1"
  function_name          = "data_load"
  description            = "Fetches API data daily and syncs it to S3 bucket"
  handler                = "data_load.lambda_handler"
  runtime                = "python3.9"
  publish                = true
  timeout                = 300
  memory_size            = 1024
  ephemeral_storage_size = 512

  create_package         = false
  local_existing_package = "./lambda_code/data_load.zip"

  attach_policy_statements = true
  policy_statements = {
    s3_bucket_access = {
      effect    = "Allow",
      actions   = ["*"],
      resources = ["*"]
    }
  }

  environment_variables = {
    S3_BUCKET_NAME = aws_s3_bucket.my_bucket.id
  }

  tags = {
    Name = "Data Load Lambda Function"
  }
}

# Lambda function to generate report
module "data_reporting" {
  source                 = "terraform-aws-modules/lambda/aws"
  version                = "8.1.1"
  function_name          = "data_reporting"
  description            = "Processes S3 data and reports analysis to CloudWatch"
  handler                = "data_reporting.lambda_handler"
  runtime                = "python3.9"
  publish                = true
  timeout                = 300
  memory_size            = 1024
  ephemeral_storage_size = 512

  attach_policy_statements = true
  policy_statements = {
    sqs = {
      effect    = "Allow",
      actions   = ["*"],
      resources = ["*"]
    }
  }

  create_package         = false
  local_existing_package = "./lambda_code/data_reporting.zip"

  environment_variables = {
    S3_BUCKET_NAME = aws_s3_bucket.my_bucket.id
  }

  tags = {
    Name = "Data Reporting Lambda Function"
  }
}
