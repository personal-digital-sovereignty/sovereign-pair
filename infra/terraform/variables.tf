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

variable "ssh_public_key" {
  type        = string
  description = "The public SSH key for user authentication on the Oracle instance"
}

variable "ssh_private_key" {
  type        = string
  description = "The corresponding private SSH key to authenticate against the OCI instance."
  sensitive   = true
}

variable "pat_ghcr" {
  type        = string
  description = "GitHub Personal Access Token for cloning private Sovereign Pair repo"
  sensitive   = true
}
variable "release_version" {
  description = "A versão do Release (Github App) a ser instalada na VM. Ex: 0.7.1, nightly"
  type        = string
  default     = "0.7.1"
}
variable "boot_volume_size_in_gbs" {
  type        = number
  description = "Size of the Boot Volume (GB). Default to 200 (Oracle Max Always Free)"
  default     = 200
}
