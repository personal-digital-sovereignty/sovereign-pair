terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }
}

provider "oci" {
  tenancy_ocid = var.tenancy_ocid
  user_ocid    = var.user_ocid
  fingerprint  = var.fingerprint
  private_key  = var.private_key
  region       = var.region
}

# ----------------------------------------------------
# Rede e Roteamento (VCN)
# ----------------------------------------------------
resource "oci_core_vcn" "sovereign_vcn" {
  compartment_id = var.compartment_ocid
  cidr_block     = "10.0.0.0/16"
  display_name   = "sovereign-cibrid-vcn"
}

resource "oci_core_internet_gateway" "igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.sovereign_vcn.id
  display_name   = "sovereign-igw"
  enabled        = true
}

resource "oci_core_default_route_table" "default_rt" {
  manage_default_resource_id = oci_core_vcn.sovereign_vcn.default_route_table_id

  route_rules {
    network_entity_id = oci_core_internet_gateway.igw.id
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
  }
}

resource "oci_core_subnet" "public_subnet" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.sovereign_vcn.id
  cidr_block     = "10.0.1.0/24"
  display_name   = "sovereign-public-subnet"
}

# Zero-Trust Security List
# Todo tráfego de entrada está fechado (Apenas ICMP Ping)
# O Tailscale contorna isso via Outbound UDP hole-punching.
resource "oci_core_default_security_list" "default_sl" {
  manage_default_resource_id = oci_core_vcn.sovereign_vcn.default_security_list_id

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
    stateless   = false
  }

  ingress_security_rules {
    protocol  = 1 # ICMP
    source    = "0.0.0.0/0"
    stateless = false
  }
}
