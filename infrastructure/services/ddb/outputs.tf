output "emr_events_table_arn" {
  value = aws_dynamodb_table.emv_events.arn
}
output "emr_events_table_name" {
  value = aws_dynamodb_table.emv_events.name
}