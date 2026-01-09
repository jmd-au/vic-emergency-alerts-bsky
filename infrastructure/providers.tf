provider "aws" {
  region                   = "ap-southeast-2"
  shared_credentials_files = ["~/.aws/credentials"]
  profile                  = "emv-terraform"
  default_tags {
    tags = {
      AccountName        = "jmd-au"
      ManagedInTerraform = "true"
      Service            = "emv"
    }
  }
}