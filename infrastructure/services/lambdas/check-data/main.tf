module "emv_alert_check_data_function" {
  source = "../../../modules/lambda_function"

  lambda_function_name        = "emv-alert-check-data"
  lambda_function_description = "EMV | Blueky Alerts - Check Data Update"
  lambda_function_role_arn    = aws_iam_role.emv_alert_check_data_role.arn
  lambda_root                 = "./${path.module}/lambda_source/"
  lambda_timeout              = 10
  lambda_memory_size          = 128
  lambda_runtime              = "python3.14"
  lambda_environment_variables = {
    DATA_LAST_UPDATED_TIMESTAMP = var.emv_data_last_updated_arn
    DATA_LAST_UPDATED_HASH      = var.emv_data_last_hash_arn
    EVENTS_LAMBDA_ARN           = var.emv_get_data_function_arn
    EVENTS_LAMBDA_NAME          = var.emv_get_data_function_name
    USER_AGENT                  = var.request_user_agent_string
    LoggingLevel                = var.lambda_log_level
  }
  lambda_layer_arns = [
    var.urllib3_layer_arn
  ]
}

resource "aws_iam_role" "emv_alert_check_data_role" {
  name = "emv-alert-check-data"
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

resource "aws_iam_role_policy_attachment" "emv_alert_check_data_lambda_execution_role" {
  role       = aws_iam_role.emv_alert_check_data_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "emv_alert_check_data_role_policy" {
  name = "emv-alert-check-data-inline"
  role = aws_iam_role.emv_alert_check_data_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:GetParameter",
          "ssm:PutParameter"
        ]
        Effect = "Allow"
        Resource = [
          var.emv_data_last_updated_arn,
          var.emv_data_last_hash_arn
        ]
      },
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect = "Allow"
        Resource = [
          var.emv_get_data_function_arn
        ]
      }
    ]
  })
}