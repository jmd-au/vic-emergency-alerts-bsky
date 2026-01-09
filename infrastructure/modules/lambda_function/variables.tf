variable "lambda_root" {
  type        = string
  description = "The relative path to the source of the lambda"
}

variable "lambda_function_name" {
  type        = string
  description = "Display name for the lambda function"
}

variable "lambda_function_description" {
  type        = string
  description = "Description to display in AWS console for lambda function"
  default     = null
  nullable    = true
}

variable "lambda_handler" {
  type        = string
  description = "The default handler within the lambda function"
  default     = "app.lambda_handler"
}

variable "lambda_runtime" {
  type        = string
  description = "Default runtime language for the lambda functions"
  default     = "python3.14"
}

variable "lambda_memory_size" {
  type        = number
  description = "Default lambda memory allocated in MB"
  default     = 128
}

variable "lambda_architectures" {
  type        = string
  description = "Default lambda architecture"
  default     = "x86_64"
}

variable "lambda_timeout" {
  type        = number
  description = "Default lambda timeout execution period"
  default     = 300
}

variable "lambda_tags" {
  type        = map(string)
  description = "Custom tags to be added to the lambda function"
  default     = {}
}

variable "lambda_environment_variables" {
  type        = map(string)
  description = "Map of environment variables to pass into the lambda runtime"
  default     = {}
}

variable "lambda_function_role_arn" {
  type        = string
  description = "ARN of the role that is to be passed to this lambda for execution"
}

variable "lambda_layer_arns" {
  type        = list(string)
  description = "List of ARNs for lambda layers to reference"
  default     = []
}