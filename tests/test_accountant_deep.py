import unittest
from src.core.the_accountant import TheAccountant

class TestTheAccountantDeepEvaluation(unittest.TestCase):

    def setUp(self):
        """Inicializa um novo motor limpo para cada teste."""
        self.engine = TheAccountant()

    def test_basic_arithmetics(self):
        """Avalia operadores nativos +, -, *, / com cast natural"""
        self.engine.register_cell("A1", "10")
        self.engine.register_cell("A2", "20")
        self.engine.register_cell("B1", "=A1+A2")
        self.engine.register_cell("B2", "=A2-A1")
        self.engine.register_cell("B3", "=A1*A2")
        self.engine.register_cell("B4", "=A2/A1")
        
        results = self.engine.evaluate_all()
        
        self.assertEqual(results.get("B1"), "30.0")
        self.assertEqual(results.get("B2"), "10.0")
        self.assertEqual(results.get("B3"), "200.0")
        self.assertEqual(results.get("B4"), "2.0")

    def test_range_aggregation_sum_avg_max_min(self):
        """Comprova a AST transformando A1:A4 em array válido"""
        self.engine.register_cell("A1", "5")
        self.engine.register_cell("A2", "10")
        self.engine.register_cell("A3", "15")
        self.engine.register_cell("A4", "20")
        
        self.engine.register_cell("C1", "=SUM(A1:A4)")
        self.engine.register_cell("C2", "=AVG(A1:A4)")
        self.engine.register_cell("C3", "=MAX(A1:A4)")
        self.engine.register_cell("C4", "=MIN(A1:A4)")
        
        results = self.engine.evaluate_all()
        
        self.assertEqual(results.get("C1"), "50.0")
        self.assertEqual(results.get("C2"), "12.5")
        self.assertEqual(results.get("C3"), "20.0")
        self.assertEqual(results.get("C4"), "5.0")

    def test_circular_dependency_protection(self):
        """A referência fechada A1->B1->C1->A1 precisa cuspir #CIRCULAR_REF! sem processamento adicional."""
        self.engine.register_cell("A1", "=B1")
        self.engine.register_cell("B1", "=C1")
        self.engine.register_cell("C1", "=A1")
        
        results = self.engine.evaluate_all()
        
        self.assertEqual(results.get("A1"), "#CIRCULAR_REF!")
        self.assertEqual(results.get("B1"), "#CIRCULAR_REF!")
        self.assertEqual(results.get("C1"), "#CIRCULAR_REF!")

    def test_delete_column_propagates_ref(self):
        """Se apagarmos a coluna A preenchida, tudo pendurado nela vira #REF!"""
        self.engine.register_cell("A1", "100")
        self.engine.register_cell("B1", "=A1*2")
        self.engine.register_cell("C1", "=B1+5")
        
        # Simula API recebendo deleção de toda a Coluna A
        updates = self.engine.handle_cell_deletion("A")
        
        # A célula A1 vai pro espaço. A B1 vira `=#REF!*2`, a C1 fica em cascata de #REF!
        results = self.engine.evaluate_all()
        
        self.assertEqual(results.get("B1"), "#REF!")
        self.assertEqual(results.get("C1"), "#REF!")

    def test_divide_by_zero(self):
        """Evita stack traceback no backend ValueError se houver div/0."""
        self.engine.register_cell("A1", "10")
        self.engine.register_cell("A2", "0")
        self.engine.register_cell("B1", "=A1/A2")
        
        results = self.engine.evaluate_all()
        self.assertEqual(results.get("B1"), "#DIV/0!")

    def test_empty_or_string_references_coercion(self):
        """Quando se aponta pra uma String (Banana) ou vazio, o casting é ZERO."""
        self.engine.register_cell("A1", "") # Célula Vazia
        self.engine.register_cell("A2", "Banana") # Texto
        self.engine.register_cell("A3", "10") # Numero
        self.engine.register_cell("B1", "=A1+A2+A3")
        self.engine.register_cell("C1", "=SUM(A1:A3)")
        
        results = self.engine.evaluate_all()
        # Vazio(0) + Banana(0) + Numero(10) = 10
        self.assertEqual(results.get("B1"), "10.0")
        self.assertEqual(results.get("C1"), "10.0")

if __name__ == '__main__':
    unittest.main()
