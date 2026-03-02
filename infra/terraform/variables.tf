variable "tenancy_ocid" {
  type        = string
  description = "The Tenancy OCID"
}

variable "user_ocid" {
  type        = string
  description = "The User OCID"
}

variable "fingerprint" {
  type        = string
  description = "The Fingerprint of the API Key"
}

variable "private_key" {
  type        = string
  description = "The Private Key for OCI API Auth"
}

variable "region" {
  type        = string
  description = "The OCI Region (e.g., sa-saopaulo-1)"
  default     = "sa-saopaulo-1"
}

variable "compartment_ocid" {
  type        = string
  description = "The Compartment OCID where resources will be created"
}

variable "tailscale_auth_key" {
  type        = string
  description = "The Tailscale Auth Key for the Node to join the mesh network"
  sensitive   = true
}
