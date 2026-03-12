import os
import sys
from sqlalchemy import create_engine, select, update
import json

from src.api.models import SystemSettings, Base
from src.config import DATABASE_URI

def fix_system_settings():
    engine = create_engine(DATABASE_URI)
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        # Check current settings
        res = conn.execute(select(SystemSettings).where(SystemSettings.tenant_id == "Jeferson"))
        settings = res.fetchone()
        
        if not settings:
            print("No settings found for Jeferson. Inserting minimal configs...")
            conn.execute(
                SystemSettings.__table__.insert().values(
                    tenant_id="Jeferson",
                    setting_key="llm_provider",
                    setting_value="ollama"
                )
            )
            return

        print("Current settings keys in DB:")
        res = conn.execute(select(SystemSettings.setting_key, SystemSettings.setting_value))
        for row in res:
            print(f"- {row.setting_key}: {row.setting_value}")
            
        print("\nFixing empty LLM provider if any...")
        conn.execute(
            update(SystemSettings).where(SystemSettings.setting_key == "llm_provider").where(SystemSettings.setting_value == "").values(setting_value="ollama")
        )
        conn.execute(
             SystemSettings.__table__.insert().values(setting_key="llm_provider", setting_value="ollama", tenant_id="Jeferson").prefix_with("OR IGNORE")
        )

if __name__ == "__main__":
    fix_system_settings()
