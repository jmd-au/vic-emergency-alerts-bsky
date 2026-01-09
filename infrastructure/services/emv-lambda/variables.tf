variable "emv_events_table_arn" {}
variable "emv_events_table_name" {}
variable "atproto_layer_arn" {}
variable "ddb_layer_arn" {}
variable "urllib3_layer_arn" {}
variable "bluesky_handle_arn" {}
variable "bluesky_secret_arn" {}

variable "lambda_log_level" {
  type        = string
  description = "Lambda Logging level - configures how much logging is put to CloudWatch"
  default     = "INFO"
  validation {
    condition     = contains(["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], var.lambda_log_level)
    error_message = "Valid values for var: lambda_log_level are (NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL)."
  }
}