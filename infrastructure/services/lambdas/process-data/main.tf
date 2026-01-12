module "emv_alert_process_data_function" {
  source = "../../../modules/lambda_function"

  lambda_function_name        = "emv-alert-process-data"
  lambda_function_description = "EMV | Blueky Alerts - Process Data"
  lambda_function_role_arn    = aws_iam_role.emv_alert_process_data_role.arn
  lambda_root                 = "./${path.module}/lambda_source"
  lambda_timeout              = 30
  lambda_memory_size          = 128
  lambda_runtime              = "python3.14"
  lambda_environment_variables = {
    EVENTS_TABLE_NAME = var.emv_events_table_name
    EVENTS_TABLE_ARN  = var.emv_events_table_arn
    EVENTS_QUEUE_URL  = var.emv_events_queue_url
    POSTS_QUEUE_URL   = var.emv_posts_queue_url
    LoggingLevel      = var.lambda_log_level
  }
  lambda_layer_arns = []
}

resource "aws_iam_role" "emv_alert_process_data_role" {
  name = "emv-alert-process-data"
  path = "/application/emv/lambda/"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "emv_alert_process_data_lambda_execution_role" {
  role       = aws_iam_role.emv_alert_process_data_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "emv_alert_process_data_role_policy" {
  name = "emv-alert-process-data-inline"
  role = aws_iam_role.emv_alert_process_data_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:BatchGetItem",
          "dynamodb:UpdateTimeToLive",
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:UpdateItem"
        ]
        Effect = "Allow"
        Resource = [
          var.emv_events_table_arn,
          "${var.emv_events_table_arn}/index/*"
        ]
      },
      {
        Action = [
          "sqs:DeleteMessage",
          "sqs:GetQueueUrl",
          "sqs:GetQueueAttributes",
          "sqs:ReceiveMessage"
        ]
        Effect = "Allow"
        Resource = [
          var.emv_events_queue_arn,
        ]
      },
      {
        Action = [
          "sqs:GetQueueUrl",
          "sqs:GetQueueAttributes",
          "sqs:SendMessage"
        ]
        Effect = "Allow"
        Resource = [
          var.emv_posts_queue_arn
        ]
      }
    ]
  })
}