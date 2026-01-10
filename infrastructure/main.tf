module "services_ddb_tables" {
  source = "./services/ddb"
}

module "lambda_layer_ddb_json" {
  source = "./lambda_layers/dynamodb-json"
}

module "lambda_layer_urllib3" {
  source = "./lambda_layers/urllib3"
}

module "lambda_layer_atproto" {
  source = "./lambda_layers/atproto"
}

module "services_sqs_queues" {
  source            = "./services/sqs"
  queue_name_prefix = "emv-bsky"
}

module "emv_check_data_lambda" {
  source = "./services/lambdas/check-data"

  emv_data_last_updated_arn       = aws_ssm_parameter.emv_data_last_updated.arn
  emv_data_last_hash_arn          = aws_ssm_parameter.emv_data_last_hash.arn
  emv_data_get_data_function_arn  = "" #module.emv_get_data_lambda.function_arn
  emv_data_get_data_function_name = "" #module.emv_get_data_lambda.function_name
  urllib3_layer_arn               = module.lambda_layer_urllib3.layer_arn
}


resource "aws_ssm_parameter" "_bluesky_handle" {
  name  = "/jmd/emv/bluesky_handle"
  type  = "SecureString"
  value = var.bluesky_handle
}

resource "aws_ssm_parameter" "_bluesky_secret" {
  name  = "/jmd/emv/bluesky_secret"
  type  = "SecureString"
  value = var.bluesky_secret
}

resource "aws_ssm_parameter" "emv_data_last_updated" {
  name  = "/jmd/emv/emv_data_last_updated"
  type  = "String"
  value = ""
}

resource "aws_ssm_parameter" "emv_data_last_hash" {
  name  = "/jmd/emv/emv_data_last_hash"
  type  = "String"
  value = ""
}

resource "aws_cloudwatch_event_rule" "emv_check_lastupdate_schedule" {
  name                = "emv_check_lastupdate_schedule"
  schedule_expression = "rate(1 minutes)"
}

resource "aws_cloudwatch_event_target" "emv_lambda_target" {
  rule      = aws_cloudwatch_event_rule.emv_check_lastupdate_schedule.name
  target_id = "lambda_target"
  arn       = module.emv_check_data_lambda.function_arn
}

resource "aws_lambda_permission" "emv_schedule_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = module.emv_check_data_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.emv_check_lastupdate_schedule.arn
}