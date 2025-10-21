# EventBridge rule to trigger data_load Lambda daily at 2 AM ET (7 AM UTC)
resource "aws_cloudwatch_event_rule" "daily_data_load" {
  name                = "daily_data_load_trigger"
  description         = "Triggers data_load Lambda daily at 2 AM ET"
  schedule_expression = "cron(30 16 * * ? *)"
}

# Permission for EventBridge to invoke the Lambda
resource "aws_lambda_permission" "allow_eventbridge_to_invoke_data_load" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.data_load.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_data_load.arn
}

# EventBridge target to call the Lambda
resource "aws_cloudwatch_event_target" "invoke_data_load_lambda" {
  rule      = aws_cloudwatch_event_rule.daily_data_load.name
  target_id = "data_load_lambda"
  arn       = module.data_load.lambda_function_arn
}

# Create SQS queue
resource "aws_sqs_queue" "s3_events_queue" {
  name                       = "s3-events-queue"
  visibility_timeout_seconds = 360 # must be > Lambda timeout (300s)
}

# Allow S3 to send messages to the SQS queue
resource "aws_sqs_queue_policy" "allow_s3_to_send" {
  queue_url = aws_sqs_queue.s3_events_queue.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "AllowS3SendMessage",
        Effect    = "Allow",
        Principal = { Service = "s3.amazonaws.com" },
        Action    = "sqs:SendMessage",
        Resource  = aws_sqs_queue.s3_events_queue.arn,
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_s3_bucket.my_bucket.arn
          }
        }
      }
    ]
  })
}

# Configure S3 bucket notification to send events to SQS
resource "aws_s3_bucket_notification" "notify_sqs_on_upload" {
  bucket = aws_s3_bucket.my_bucket.id

  queue {
    queue_arn = aws_sqs_queue.s3_events_queue.arn
    events    = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_sqs_queue_policy.allow_s3_to_send]
}

# Give Lambda permission to read messages from the SQS queue
resource "aws_lambda_event_source_mapping" "trigger_data_reporting_from_sqs" {
  event_source_arn = aws_sqs_queue.s3_events_queue.arn
  function_name    = module.data_reporting.lambda_function_name
  batch_size       = 1
  enabled          = true
}

# Allow SQS to invoke the Lambda
resource "aws_lambda_permission" "allow_sqs_to_invoke_reporting" {
  statement_id  = "AllowSQSTrigger"
  action        = "lambda:InvokeFunction"
  function_name = module.data_reporting.lambda_function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.s3_events_queue.arn
}
