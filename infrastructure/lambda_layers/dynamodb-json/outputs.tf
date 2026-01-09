output "layer_arn" {
  value = aws_lambda_layer_version.dynamodb_json.arn
}