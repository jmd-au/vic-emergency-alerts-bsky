locals {
  requirements_path = "${path.module}/lambda_source/requirements.txt"
  zip_output_path   = "atproto.zip"
}

resource "aws_lambda_layer_version" "atproto" {
  filename     = data.archive_file.lambda_layer_zip.output_path
  layer_name   = "atproto-library"
  description  = "atproto@2.2.3"
  license_info = "MIT License - https://spdx.org/licenses/MIT"

  compatible_architectures = ["x86_64"]
  compatible_runtimes      = ["python3.14"]
  depends_on               = [terraform_data.lambda_layer_dependencies, data.archive_file.lambda_layer_zip]
}

resource "terraform_data" "lambda_layer_dependencies" {
  triggers_replace = {
    every_time = timestamp()
    # dependencies_versions = filemd5("${local.requirements_path}")
  }
  provisioner "local-exec" {
    command = <<EOT
      which python3
      python3 --version
      rm -rf python
      mkdir -p python/python
      cd python/python
      pip3 install -r ../../${local.requirements_path} -t ./
    EOT
  }
}

data "archive_file" "lambda_layer_zip" {
  type             = "zip"
  source_dir       = "python"
  output_path      = local.zip_output_path
  output_file_mode = "0666"

  depends_on = [terraform_data.lambda_layer_dependencies]
}