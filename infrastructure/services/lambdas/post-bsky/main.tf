module "emv_alert_post_bsky_function" {
  source = "../../../modules/lambda_function"

  lambda_function_name        = "emv-alert-post-bsky"
  lambda_function_description = "EMV | Blueky Alerts ATProto"
  lambda_function_role_arn    = aws_iam_role.emv_alert_post_bsky_role.arn
  lambda_root                 = "./${path.module}/lambda_source/"
  lambda_timeout              = 30
  lambda_memory_size          = 128
  lambda_runtime              = "python3.14"
  lambda_environment_variables = {
    TABLE_NAME       = var.emv_events_table_name
    BSKY_HANDLE      = var.bluesky_handle_arn
    BSKY_SECRET      = var.bluesky_secret_arn
    BSKY_JWT         = var.bluesky_jwt_arn
    BSKY_REFRESH_JWT = var.bluesky_refresh_jwt_arn
    LoggingLevel     = var.lambda_log_level
  }
  lambda_layer_arns = [
    var.urllib3_layer_arn
  ]
}

resource "aws_iam_role" "emv_alert_post_bsky_role" {
  name = "emv-alert-post-bsky"
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

resource "aws_iam_role_policy_attachment" "emv_alert_post_bsky_lambda_execution_role" {
  role       = aws_iam_role.emv_alert_post_bsky_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "emv_alert_post_bsky_role_policy" {
  name = "emv-alert-post-bsky-inline"
  role = aws_iam_role.emv_alert_post_bsky_role.id
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
          "sqs:ReceiveMessage",
          "sqs:SendMessage"
        ]
        Effect = "Allow"
        Resource = [
          var.emv_posts_queue_arn
        ]
      },
      {
        Action = [
          "ssm:GetParameter"
        ]
        Effect = "Allow"
        Resource = [
          var.bluesky_handle_arn,
          var.bluesky_secret_arn
        ]
      },
      {
        Action = [
          "ssm:GetParameter",
          "ssm:PutParameter"
        ]
        Effect = "Allow"
        Resource = [
          var.bluesky_jwt_arn,
          var.bluesky_refresh_jwt_arn
        ]
      }
    ]
  })
}