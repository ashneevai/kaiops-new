terraform {
  required_version = ">= 1.8.0"
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "kaiops" {
  name     = "rg-kaiops-prod"
  location = "East US"
}
