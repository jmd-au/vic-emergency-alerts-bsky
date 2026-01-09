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

module "emv_events_lambda" {
  source = "./services/emv-lambda"

  emv_events_table_arn  = module.services_ddb_tables.emr_events_table_arn
  emv_events_table_name = module.services_ddb_tables.emr_events_table_name
  atproto_layer_arn     = module.lambda_layer_atproto.layer_arn
  ddb_layer_arn         = module.lambda_layer_ddb_json.layer_arn
  urllib3_layer_arn     = module.lambda_layer_urllib3.layer_arn
  bluesky_handle_arn    = aws_ssm_parameter._bluesky_handle.arn
  bluesky_secret_arn    = aws_ssm_parameter._bluesky_secret.arn
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

resource "aws_cloudwatch_event_rule" "emr_lambda_schedule" {
  name                = "emr_lambda_schedule"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "emr_lambda_target" {
  rule      = aws_cloudwatch_event_rule.emr_lambda_schedules.name
  target_id = "lambda_target"
  arn       = module.emv_events_lambda.function_arn
}

resource "aws_lambda_permission" "emr_schedule_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = module.emv_events_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.emr_lambda_schedule.arn
}