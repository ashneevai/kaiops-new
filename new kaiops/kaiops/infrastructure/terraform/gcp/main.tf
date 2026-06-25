terraform {
  required_version = ">= 1.8.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

resource "google_compute_network" "kaiops" {
  name                    = "kaiops-network"
  auto_create_subnetworks = false
}
