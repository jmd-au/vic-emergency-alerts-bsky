variable "emv_events_table_arn" {}
variable "emv_events_table_name" {}
variable "emv_events_queue_url" {}
variable "emv_events_queue_arn" {}
variable "emv_posts_queue_url" {}
variable "emv_posts_queue_arn" {}
variable "ddb_layer_arn" {}

variable "lambda_log_level" {
  type        = string
  description = "Lambda Logging level - configures how much logging is put to CloudWatch"
  default     = "INFO"
  validation {
    condition     = contains(["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], var.lambda_log_level)
    error_message = "Valid values for var: lambda_log_level are (NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL)."
  }
}