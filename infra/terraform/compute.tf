data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_ocid
}

data "oci_core_images" "ubuntu_arm" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "22.04"
  shape                    = "VM.Standard.A1.Flex"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

resource "oci_core_instance" "the_coder" {
  # Restaurando para o AD-1 original (Index [0])
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_ocid
  display_name        = "sovereign-coder-node"
  shape               = "VM.Standard.A1.Flex"

  # Using Paid Tier configuration (Pay As You Go)
  shape_config {
    ocpus         = 6
    memory_in_gbs = 32
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public_subnet.id
    display_name     = "sovereign-coder"
    hostname_label   = "sovereign-coder"
    assign_public_ip = true
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu_arm.images[0].id
    # Ensure enough disk space for heavy LLMs (Free tier gives up to 200GB total across block volumes)
    boot_volume_size_in_gbs = 50
  }

  metadata = {
    user_data = base64encode(templatefile("${path.module}/cloud-init.yaml", {
      tailscale_auth_key = var.tailscale_auth_key
      ssh_public_key     = var.ssh_public_key
      pat_ghcr           = var.pat_ghcr
    }))
  }

  lifecycle {
    ignore_changes = [
      source_details,  # Previne erro de kmsKeyId vazio em atualizações
    ]
  }
}

output "coder_public_ip" {
  value       = oci_core_instance.the_coder.public_ip
  description = "O IP Publico apenas de fachada (Bloqueado por Firewall Zero-Trust)"
}
