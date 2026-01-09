locals {
  default_tags = {
    Module = "lambda_function"
  }
}


resource "terraform_data" "replacement_requirements" {
  input = filemd5("${var.lambda_root}/requirements.txt")
}

resource "terraform_data" "replacement_source" {
  input = filemd5("${var.lambda_root}/app.py")
}
resource "terraform_data" "install_dependencies" {
  provisioner "local-exec" {
    command = "pip install -r ${var.lambda_root}/requirements.txt -t ${var.lambda_root}/"
  }
  lifecycle {
    replace_triggered_by = [
      terraform_data.replacement_requirements,
      terraform_data.replacement_source
    ]
  }
}

data "archive_file" "lambda_source" {
  depends_on = [terraform_data.install_dependencies]
  excludes = [
    "__pycache__",
    "venv",
    "requirements.txt"
  ]

  source_dir       = var.lambda_root
  output_path      = "${var.lambda_function_name}.zip"
  type             = "zip"
  output_file_mode = "0666"
}

resource "aws_lambda_function" "lambda_function" {
  function_name    = var.lambda_function_name
  description      = var.lambda_function_description
  role             = var.lambda_function_role_arn
  filename         = data.archive_file.lambda_source.output_path
  source_code_hash = data.archive_file.lambda_source.output_base64sha256
  architectures    = [var.lambda_architectures]
  handler          = var.lambda_handler
  runtime          = var.lambda_runtime
  layers           = var.lambda_layer_arns
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory_size

  dynamic "environment" {
    for_each = length(keys(var.lambda_environment_variables)) == 0 ? [] : [true]
    content {
      variables = var.lambda_environment_variables
    }
  }

  lifecycle {
    replace_triggered_by = [
      terraform_data.replacement_requirements,
      terraform_data.replacement_source
    ]
  }

  tags = merge(
    local.default_tags,
    var.lambda_tags,
    {}
  )
}

resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = "30"
  tags = merge(
    local.default_tags,
    var.lambda_tags,
    {}
  )
}