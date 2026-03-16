from src.core.the_accountant import TheAccountant

def test_static_values():
    """Valores numéricos simples e Textos sem fórmula."""
    engine = TheAccountant()
    engine.register_cell("A1", "10")
    engine.register_cell("B1", "25.5")
    engine.register_cell("C1", "Hello")
    
    results = engine.evaluate_all()
    
    assert results["A1"] == "10.0"
    assert results["B1"] == "25.5"
    assert results["C1"] == "#VALUE!" # Non-numeric fallbacks to #VALUE! for math safety

def test_simple_addition():
    """Somas simples e referências unitárias."""
    engine = TheAccountant()
    engine.register_cell("A1", "10")
    engine.register_cell("A2", "20")
    engine.register_cell("A3", "=A1+A2")
    engine.register_cell("B1", "=A3")
    
    results = engine.evaluate_all()
    
    assert results["A3"] == "30.0"
    assert results["B1"] == "30.0"

def test_circular_reference():
    """Prevenção de loop infinito via Exception customizada."""
    engine = TheAccountant()
    engine.register_cell("A1", "=B1")
    engine.register_cell("B1", "=A1")
    
    results = engine.evaluate_all()
    
    assert results["A1"] == "#CIRCULAR_REF!"
    assert results["B1"] == "#CIRCULAR_REF!"

def test_division_by_zero():
    """Tratamento de divisão por Zero numérico e propagação de #DIV/0!"""
    engine = TheAccountant()
    engine.register_cell("A1", "10")
    engine.register_cell("A2", "0")
    engine.register_cell("A3", "=A1/A2")
    
    results = engine.evaluate_all()
    
    assert results["A3"] == "#DIV/0!"

def test_referential_deletion_cascade():
    """Testa o colapso e bloqueio de fórmula se um Node dependente for apagado."""
    engine = TheAccountant()
    engine.register_cell("C1", "100")
    engine.register_cell("D1", "=C1+50")
    engine.register_cell("E1", "=D1*2")
    
    # Simula o Frontend deletando a Coluna C
    cascade = engine.handle_cell_deletion("C")
    
    # E1 depende de D1 que depende de C1. A Deleção de C afeta a árvore toda.
    affected_nodes = [n[0] for n in cascade]
    assert "D1" in affected_nodes
    assert "E1" in affected_nodes
    
    results = engine.evaluate_all()
    assert results["D1"] == "#REF!"
    assert results["E1"] == "#REF!"
