import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Set dummy master key for test (64 hex characters = 32 bytes)
os.environ["SOVEREIGN_MASTER_KEK"] = "0" * 64

from sqlalchemy import text
from src.api.database import Base, engine, get_db
from src.api.models import SystemSettings

def test_db():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    
    # Clean up any existing
    db.query(SystemSettings).filter(SystemSettings.setting_key == "OPENAI_API_KEY", SystemSettings.tenant_id == "test_encrypted").delete()
    db.commit()

    # Insert using ORM
    setting = SystemSettings(setting_key="OPENAI_API_KEY", setting_value="sk-proj-super-secret-123", tenant_id="test_encrypted")
    db.add(setting)
    db.commit()
    db.refresh(setting)

    # Raw check
    raw_val = db.execute(text("SELECT setting_value FROM system_settings WHERE setting_key='OPENAI_API_KEY' AND tenant_id='test_encrypted'")).scalar()
    print("Raw DB Value (Encrypted):", raw_val)

    # ORM check
    retrieved = db.query(SystemSettings).filter(SystemSettings.setting_key == "OPENAI_API_KEY", SystemSettings.tenant_id == "test_encrypted").first()
    print("ORM Decrypted Value:", retrieved.setting_value)
    
    # Compare
    assert "sk-proj-super-secret-123" not in str(raw_val), "The raw value should NOT contain the secret"
    assert retrieved.setting_value == "sk-proj-super-secret-123", "The ORM should automatically decrypt the value"

if __name__ == "__main__":
    test_db()
    print("SUCCESS: Encryption and Decryption at rest works seamlessly!")
