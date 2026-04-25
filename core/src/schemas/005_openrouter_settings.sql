-- ============================================================================
-- SOVEREIGN PAIR - OPENROUTER SETTINGS LAYER
-- ============================================================================

INSERT OR IGNORE INTO global_settings (id, value_json) VALUES (
    'openrouter',
    '{
        "api_key": "",
        "base_url": "https://openrouter.ai/api/v1",
        "site_url": "https://sovereign.pair",
        "site_name": "Sovereign Pair",
        "enabled": false,
        "default_model": "google/gemini-pro-1.5",
        "fallback_enabled": true
    }'
);
