terraform {
  required_version = ">= 1.8.0"
}

provider "aws" {
  region = var.region
}

variable "region" {
  type    = string
  default = "us-east-1"
}

resource "aws_vpc" "kaiops" {
  cidr_block = "10.60.0.0/16"
  tags = { Name = "kaiops-vpc" }
}
