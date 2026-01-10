variable "emv_data_last_updated_arn" {}
variable "emv_data_last_hash_arn" {}
variable "emv_data_get_data_function_arn" {}
variable "emv_data_get_data_function_name" {}
variable "urllib3_layer_arn" {}

variable "lambda_log_level" {
  type        = string
  description = "Lambda Logging level - configures how much logging is put to CloudWatch"
  default     = "INFO"
  validation {
    condition     = contains(["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], var.lambda_log_level)
    error_message = "Valid values for var: lambda_log_level are (NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL)."
  }
}