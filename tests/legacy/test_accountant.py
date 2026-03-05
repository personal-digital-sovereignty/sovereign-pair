from src.core.the_accountant import TheAccountant

engine = TheAccountant()
engine.register_cell("A1", "10")
engine.register_cell("B1", "20")
engine.register_cell("C1", "=SUM(A1:B1)")
engine.register_cell("C2", "=AVG(A1:B1)")
engine.register_cell("D1", "=MAX(A1:C1)")

results = engine.evaluate_all()
print("Results:", results)
