import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from src.core.the_mom import should_use_polling, get_ignores
from src.core.the_nurse import TheNurse

# ----------------- The Mom Tests -----------------

def test_the_mom_os_sniffing():
    """Testa se The Mom consegue detectar quando usar Polling."""
    polling = should_use_polling()
    assert isinstance(polling, bool)

def test_the_mom_ignores_parser(tmp_path):
    """Testa o File Watcher lendo `.sovereignignore`."""
    vault_dir = tmp_path / "test_vault"
    vault_dir.mkdir()
    
    ignore_file = vault_dir / ".sovereignignore"
    ignore_file.write_text("custom_ignore_dir\n# comment\n")
    
    ignores = get_ignores(str(vault_dir))
    
    assert "custom_ignore_dir" in ignores
    assert "node_modules" in ignores  # default
    assert ".venv" in ignores         # default
    assert "# comment" not in ignores # ignora comentários

# ----------------- The Nurse Tests -----------------

@pytest.mark.asyncio
@patch("src.engine_builder.resolve_dynamic_llm")
async def test_the_nurse_intent_evaluation(mock_resolve_llm):
    """Testa se The Nurse roteia intenções corretamente sem bater no Ollama."""
    mock_llm_instance = MagicMock()
    mock_response = MagicMock()
    json_payload = "```json\n{\n  \"action\": \"format_table\",\n  \"task_type\": \"format_table\"\n}\n```"
    mock_response.message.content = json_payload
    mock_response.__str__.return_value = json_payload
    mock_llm_instance.achat = AsyncMock(return_value=mock_response)
    mock_resolve_llm.return_value = mock_llm_instance

    nurse = TheNurse("ollama", "llama3.2:latest")
    
    # Executa avaliação
    result = await nurse.evaluate_intent("Extraia a lista em Markdown.")
    
    # O LLM Mockado devolve format_table
    assert result.get("action") == "format_table"

# ----------------- The Doctor Tests -----------------
# The Doctor relies heavily on Streaming FastApi dependencies.
# Its API endpoint (/v1/chat) is already covered in the integration API suites,
# but we can assert the class isolation here if needed in the future.
def test_the_doctor_instantiation():
    """Garante estruturalmente que The Doctor existe no repositório."""
    try:
        from src.core.the_doctor import TheDoctor
        assert True
    except ImportError:
        pytest.fail("The Doctor class not found or broken.")
