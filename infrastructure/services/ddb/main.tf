resource "aws_dynamodb_table" "emv_events" {
  name                        = "emv_events"
  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = true
  hash_key                    = "EventId"

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  attribute {
    name = "EventId"
    type = "S"
  }

}