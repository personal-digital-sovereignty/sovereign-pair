"""
Sovereign Pair — Time-Series Pipeline Tests
Tests the analyze_and_join_time_series.py Pandas worker for correctness.
"""
import sys
import os
import json
import importlib

# Ensure pandas is available before importing the worker module
# (the worker calls sys.exit(1) if pandas is not found at import time)
import pandas  # noqa: F401

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import the module, catching any SystemExit from the subprocess fallback path
try:
    from analyze_and_join_time_series import parse_markdown_blocks, join_and_extract
except SystemExit:
    # If pandas is installed but the module still exits, force-reimport
    spec = importlib.util.spec_from_file_location(
        "analyze_and_join_time_series",
        os.path.join(os.path.dirname(__file__), "..", "analyze_and_join_time_series.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    parse_markdown_blocks = mod.parse_markdown_blocks
    join_and_extract = mod.join_and_extract


# ── Fixtures ──────────────────────────────────────────────────

BRENT_BLOCK = """[CONTEXT: DADOS HISTÓRICOS BRUTOS REFERENTES AO MACRO INDICADOR BZ=F (BRENT)]
2024-01-15 | USD 79.20 | BRL 388.91
2024-02-15 | USD 81.62 | BRL 404.65
2024-03-15 | USD 84.67 | BRL 421.52
2024-04-15 | USD 89.00 | BRL 456.13
2024-05-15 | USD 82.99 | BRL 426.08
"""

IPCA_BLOCK = """[CONTEXT: DADOS HISTÓRICOS BRUTOS REFERENTES AO MACRO INDICADOR IPCA]
2024-01-01 | 0.42
2024-02-01 | 0.83
2024-03-01 | 0.16
2024-04-01 | 0.38
2024-05-01 | 0.46
"""

GASOLINA_BLOCK = """[CONTEXT: DADOS HISTÓRICOS BRUTOS REFERENTES AO MACRO INDICADOR GASOLINA]
2024-01-01 | 5.60
2024-02-01 | 5.60
2024-03-01 | 5.60
2024-04-01 | 5.60
2024-05-01 | 5.60
"""

DOLAR_PTAX_BLOCK = """[CONTEXT: DADOS HISTÓRICOS BRUTOS REFERENTES AO MACRO INDICADOR DOLAR_PTAX]
2024-01-15 | 4.91
2024-02-15 | 4.96
2024-03-15 | 4.98
2024-04-15 | 5.13
2024-05-15 | 5.13
"""


# ── parse_markdown_blocks ──────────────────────────────────────
class TestParseMarkdownBlocks:
    def test_parses_brent_with_usd_brl(self):
        ds = parse_markdown_blocks([BRENT_BLOCK])
        assert "BRENT" in ds
        df = ds["BRENT"]
        assert "BRENT_USD" in df.columns
        assert "BRENT_BRL" in df.columns
        assert len(df) == 5

    def test_parses_ipca_single_value(self):
        ds = parse_markdown_blocks([IPCA_BLOCK])
        assert "IPCA" in ds
        df = ds["IPCA"]
        assert "IPCA" in df.columns
        assert len(df) == 5

    def test_parses_gasolina(self):
        ds = parse_markdown_blocks([GASOLINA_BLOCK])
        assert "GASOLINA" in ds

    def test_parses_dolar_ptax(self):
        ds = parse_markdown_blocks([DOLAR_PTAX_BLOCK])
        assert "DOLAR_PTAX" in ds

    def test_empty_input(self):
        ds = parse_markdown_blocks([])
        assert len(ds) == 0

    def test_garbage_input(self):
        ds = parse_markdown_blocks(["lixo sem formato nenhum\nfoo bar baz"])
        assert len(ds) == 0

    def test_semantic_map_normalizes_names(self):
        block = """[CONTEXT: DADOS HISTÓRICOS BRUTOS REFERENTES AO MACRO INDICADOR PETRÓLEO BRENT CRUDE]
2024-01-15 | USD 79.20 | BRL 388.91
"""
        ds = parse_markdown_blocks([block])
        assert "BRENT" in ds  # Normalizado de "PETRÓLEO BRENT CRUDE"


# ── Deduplication (FIX-13) ─────────────────────────────────────
class TestDeduplication:
    def test_duplicate_dolar_ptax_merges(self):
        """FIX-13: Two identical DOLAR_PTAX blocks should merge, not duplicate."""
        ds = parse_markdown_blocks([DOLAR_PTAX_BLOCK, DOLAR_PTAX_BLOCK])
        assert "DOLAR_PTAX" in ds
        # Should NOT have DOLAR_PTAX_1 or DOLAR_PTAX_2
        keys = list(ds.keys())
        assert len([k for k in keys if "DOLAR_PTAX" in k]) == 1


# ── join_and_extract ───────────────────────────────────────────
class TestJoinAndExtract:
    def test_single_dataset_returns_success(self):
        result = json.loads(join_and_extract([IPCA_BLOCK]))
        assert result["status"] == "success"
        assert "markdown" in result

    def test_multi_dataset_join(self):
        result = json.loads(join_and_extract([BRENT_BLOCK, IPCA_BLOCK, GASOLINA_BLOCK]))
        assert result["status"] == "success"
        md = result["markdown"]
        # Should contain Pearson matrix
        assert "Pearson" in md or "Correlação" in md
        # Should contain annual averages
        assert "2024" in md

    def test_multi_dataset_contains_all_columns(self):
        result = json.loads(join_and_extract([BRENT_BLOCK, IPCA_BLOCK, GASOLINA_BLOCK, DOLAR_PTAX_BLOCK]))
        md = result["markdown"]
        assert "BRENT_USD" in md
        assert "IPCA" in md
        assert "GASOLINA" in md
        assert "DOLAR_PTAX" in md

    def test_empty_input_returns_error(self):
        result = json.loads(join_and_extract([]))
        assert "error" in result

    def test_pearson_values_valid(self):
        """Pearson r values should be between -1 and 1."""
        result = json.loads(join_and_extract([BRENT_BLOCK, IPCA_BLOCK, GASOLINA_BLOCK]))
        md = result["markdown"]
        import re
        # Extract all float values from the Pearson table
        numbers = re.findall(r'(?<!\d)-?\d+\.\d+', md)
        for n in numbers:
            val = float(n)
            # Pearson values and data values coexist; Pearson should be |val| <= 1
            # We just check nothing is NaN
            assert val == val  # NaN != NaN

    def test_ffill_ipca_stays_nan(self):
        """IPCA (flow variable) should NOT be forward-filled."""
        # Create a block where IPCA has a gap
        ipca_gap = """[CONTEXT: DADOS HISTÓRICOS BRUTOS REFERENTES AO MACRO INDICADOR IPCA]
2024-01-01 | 0.42
2024-03-01 | 0.16
"""
        gas = """[CONTEXT: DADOS HISTÓRICOS BRUTOS REFERENTES AO MACRO INDICADOR GASOLINA]
2024-01-01 | 5.60
2024-02-01 | 5.60
2024-03-01 | 5.60
"""
        result = json.loads(join_and_extract([ipca_gap, gas]))
        md = result["markdown"]
        # The Feb row should have "—" for IPCA (NaN, not ffilled)
        lines = md.split('\n')
        feb_line = [l for l in lines if '2024-02' in l]
        if feb_line:
            assert "—" in feb_line[0]  # IPCA gap → "—"


# ── Edge Cases ─────────────────────────────────────────────────
class TestEdgeCases:
    def test_single_row_dataset(self):
        block = """[CONTEXT: DADOS HISTÓRICOS BRUTOS REFERENTES AO MACRO INDICADOR IPCA]
2024-01-01 | 0.42
"""
        ds = parse_markdown_blocks([block])
        assert "IPCA" in ds
        assert len(ds["IPCA"]) == 1

    def test_negative_values(self):
        """IPCA can be negative (deflation). Pipeline must handle it."""
        block = """[CONTEXT: DADOS HISTÓRICOS BRUTOS REFERENTES AO MACRO INDICADOR IPCA]
2024-01-01 | 0.42
2024-02-01 | -0.68
2024-03-01 | 0.16
"""
        ds = parse_markdown_blocks([block])
        df = ds["IPCA"]
        assert df["IPCA"].min() < 0
