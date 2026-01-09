module "emv_alert_function" {
  source = "../../modules/lambda_function"

  lambda_function_name        = "emv-alert"
  lambda_function_description = "EMV | Blueky Alerts ATProto"
  lambda_function_role_arn    = aws_iam_role.emv_alert_role.arn
  lambda_root                 = "./${path.module}/lambda_source/"
  lambda_timeout              = 30
  lambda_memory_size          = 128
  lambda_runtime              = "python3.14"
  lambda_environment_variables = {
    TABLE_NAME   = var.emv_events_table_name
    LoggingLevel = var.lambda_log_level
  }
  lambda_layer_arns = [
    var.atproto_layer_arn,
    var.ddb_layer_arn,
    var.urllib3_layer_arn
  ]
}

resource "aws_iam_role" "emv_alert_role" {
  name = "emv-alert"
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

resource "aws_iam_role_policy_attachment" "emv_alert_lambda_execution_role" {
  role       = aws_iam_role.emv_alert_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "emv_alert_role_policy" {
  name = "emv-alert-inline"
  role = aws_iam_role.emv_alert_role.id
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
          "ssm:GetParameter"
        ]
        Effect = "Allow"
        Resource = [
          var.bluesky_handle_arn,
          var.bluesky_secret_arn
        ]
      }
    ]
  })
}