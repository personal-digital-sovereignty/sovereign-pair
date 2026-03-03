import oci
import os
import tempfile

private_key = """-----BEGIN RSA PRIVATE KEY-----
""" + os.environ.get('OCI_PRIVATE_KEY_BODY', '') + """
-----END RSA PRIVATE KEY-----"""

# Create temp pem file
fd, path = tempfile.mkstemp(suffix='.pem')
with os.fdopen(fd, 'w') as f:
    f.write(private_key)

config = {
    "user": os.environ.get('OCI_USER_OCID'),
    "key_file": path,
    "fingerprint": os.environ.get('OCI_FINGERPRINT'),
    "tenancy": os.environ.get('OCI_TENANCY_OCID'),
    "region": os.environ.get('OCI_REGION', 'us-ashburn-1')
}

try:
    print("Testing Auth...")
    identity = oci.identity.IdentityClient(config)
    user = identity.get_user(config['user']).data
    print(f"SUCCESS! Authenticated as: {user.description}")
except Exception as e:
    print(f"FAILED! Error: {str(e)}")
finally:
    os.remove(path)
