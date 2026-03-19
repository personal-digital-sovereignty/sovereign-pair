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
    boot_volume_size_in_gbs = var.boot_volume_size_in_gbs
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
      metadata,        # Previne DESTRUIÇÃO da instância A1 existente ao mudar o cloud-init.yaml
    ]
  }
}

output "coder_public_ip" {
  value       = oci_core_instance.the_coder.public_ip
  description = "O IP Publico apenas de fachada (Bloqueado por Firewall Zero-Trust)"
}

resource "null_resource" "deploy_release" {
  triggers = {
    release_version = var.release_version
    instance_id     = oci_core_instance.the_coder.id
  }

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = var.ssh_private_key
    host        = oci_core_instance.the_coder.public_ip
    timeout     = "5m"
  }

  provisioner "remote-exec" {
    inline = [
      "echo 'Waiting for cloud-init to finish (if newly created)...'",
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do sleep 5; done",
      "echo 'Deploying Sovereign Pair Release: ${var.release_version}'",
      "sudo systemctl stop sovereign || true",
      "mkdir -p /tmp/sovereign",
      "cd /tmp/sovereign",
      "export GH_TOKEN=${var.pat_ghcr}",
      "if ! command -v gh &> /dev/null; then echo \"Installing GitHub CLI (gh)...\"; sudo mkdir -p -m 755 /etc/apt/keyrings && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && echo \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main\" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null && sudo apt-get update && sudo apt-get install gh -y; fi",
      "gh release download ${var.release_version} -R Personal-Digital-Sovereignty/sovereign-pair -p sovereign-core-linux-arm64-binary -O sovereign-core",
      "chmod +x sovereign-core",
      "sudo mv sovereign-core /usr/local/bin/sovereign-core",
      "sudo systemctl daemon-reload",
      "sudo systemctl enable sovereign",
      "sudo systemctl start sovereign",
      "echo 'Deployment successful!'"
    ]
  }
}
