import os
import oci

# Load config from environment or default location
# We will create a dummy config structure to test the raw key
config = {
    "user": os.environ.get("OCI_USER_OCID"),
    "key_file": "/home/jefersonlopes/Downloads/jefersonlopes.br@gmail.com-2026-03-02T22_44_26.726Z.pem",
    "fingerprint": os.environ.get("OCI_FINGERPRINT"),
    "tenancy": os.environ.get("OCI_TENANCY_OCID"),
    "region": "us-ashburn-1"
}

try:
    print(f"Testing OCI Authentication for user: {config['user']}")
    print(f"Using key file: {config['key_file']}")
    
    # Initialize identity client
    identity = oci.identity.IdentityClient(config)
    
    # Simple test: list availability domains
    ads = identity.list_availability_domains(config["tenancy"])
    print("\n✅ SUCCESS! Authentication working.")
    print("Availability Domains found:")
    for ad in ads.data:
        print(f" - {ad.name}")
        
except Exception as e:
    print("\n❌ FAILED! Authentication error:")
    print(str(e))
