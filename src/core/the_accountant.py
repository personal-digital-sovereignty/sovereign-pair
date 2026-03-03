import ast
import operator
import re
from typing import Dict, List, Set, Tuple, Any

class DependencyGraph:
    """
    Grafo Acíclico Dirigido (DAG) para gerenciamento de dependências de células
    de tabelas Markdown.
    
    Proteção Mítica: Previne loops infinitos (Referências Circulares) e resolve
    A cascata de `#REF!` quando colunas/linhas fonte são deletadas do Front-End.
    """
    def __init__(self):
        # adjacency_list[node] = list of nodes that depend on 'node'
        self.adjacency_list: Dict[str, Set[str]] = {}
        # reverse_adj[node] = list of nodes that 'node' depends on
        self.reverse_adj: Dict[str, Set[str]] = {}

    def add_dependency(self, target: str, source: str):
        """target (ex: C1) depends on source (ex: A1)"""
        if source not in self.adjacency_list:
            self.adjacency_list[source] = set()
        if target not in self.reverse_adj:
            self.reverse_adj[target] = set()
            
        self.adjacency_list[source].add(target)
        self.reverse_adj[target].add(source)

    def remove_node(self, node: str) -> List[str]:
        """
        Usuario deletou a Coluna de `node`. 
        Retorna lista de TODOS OS dependentes (diretos e indiretos) que vão quebrar e virar `#REF!`.
        """
        affected = set()
        queue = [node]
        
        while queue:
            current = queue.pop(0)
            direct_deps = self.adjacency_list.get(current, [])
            for dep in direct_deps:
                if dep not in affected:
                    affected.add(dep)
                    queue.append(dep)

        # Limpa os elos do nó deletado
        self.adjacency_list.pop(node, None)
        if node in self.reverse_adj:
            for source in self.reverse_adj[node]:
                if source in self.adjacency_list and node in self.adjacency_list[source]:
                    self.adjacency_list[source].remove(node)
            self.reverse_adj.pop(node, None)
            
        return list(affected)

    def detect_cycle(self, start_node: str, visited: Set[str] | None = None, stack: Set[str] | None = None) -> bool:
        """Detecta erro de referência circular se A depende de B e B depende de A"""
        if visited is None:
            visited = set()
        if stack is None:
            stack = set()
            
        visited.add(start_node)
        stack.add(start_node)

        for neighbor in self.adjacency_list.get(start_node, []):
            if neighbor not in visited:
                if self.detect_cycle(neighbor, visited, stack):
                    return True
            elif neighbor in stack:
                return True
                
        stack.remove(start_node)
        return False

class CellNode:
    def __init__(self, coordinate: str, raw_content: str):
        self.coordinate = coordinate
        self.raw_content = raw_content
        self.is_formula = raw_content.startswith("=")
        self.value: Any = None
        self.parsed_formula = None

class TheAccountant:
    """
    The Accountant: Motor Aritmético e AST Parser
    Responsável por interpretar Fórmulas Sensus, resolver ranges (A1:B2)
    e invocar a Matemática.
    """
    
    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }
    
    ALLOWED_FUNCTIONS = {
        "SUM": sum,
        "MAX": max,
        "MIN": min,
        "AVG": lambda args: sum(args) / len(args) if args else 0
    }

    def __init__(self):
        self.cells: Dict[str, CellNode] = {}
        self.dag = DependencyGraph()
        
    def _parse_range(self, range_str: str) -> List[str]:
        """
        Converte 'A1:B3' para ['A1', 'A2', 'A3', 'B1', 'B2', 'B3']
        """
        match = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", range_str)
        if not match:
            return [range_str]
            
        start_col, start_row = match.group(1), int(match.group(2))
        end_col, end_row = match.group(3), int(match.group(4))
        
        def col2num(col_str):
            num = 0
            for c in col_str:
                num = num * 26 + (ord(c.upper()) - ord('A') + 1)
            return num
            
        def num2col(num):
            string = ""
            while num > 0:
                num, remainder = divmod(num - 1, 26)
                string = chr(65 + remainder) + string
            return string

        min_col, max_col = sorted([col2num(start_col), col2num(end_col)])
        min_row, max_row = sorted([start_row, end_row])
        
        cells = []
        for c in range(min_col, max_col + 1):
            col_str = num2col(c)
            for r in range(min_row, max_row + 1):
                cells.append(f"{col_str}{r}")
                
        return cells

    def register_cell(self, coordinate: str, content: str):
        """Registra a Célula Virtual na Memória do DAG"""
        node = CellNode(coordinate, content)
        self.cells[coordinate] = node
        
        if node.is_formula:
            # Extrair referencias ex =SUM(A1:A3) ou =A1+B1
            formula_internal = content[1:] # Tira o `=`
            # Usando Regex Simples pra extrair `A1` ou `A1:B2` (Provisório)
            refs = re.findall(r"([A-Z]+\d+(?::[A-Z]+\d+)?)", formula_internal)
            
            for ref in refs:
                if ":" in ref:
                    expanded = self._parse_range(ref)
                    for e in expanded:
                        self.dag.add_dependency(target=coordinate, source=e)
                else:
                    self.dag.add_dependency(target=coordinate, source=ref)
                    
            if self.dag.detect_cycle(coordinate):
                node.value = "#CIRCULAR_REF!"

    def handle_cell_deletion(self, deleted_column: str) -> List[Tuple[str, str]]:
        """
        Quando uma Coluna inteira é apagada e o Front Notifica:
        Identifica todas as células que começam com essa coluna (ex: "C" -> "C1", "C2"),
        remove-as do DAG e converte todos os dependentes para #REF!
        """
        affected_nodes = []
        for coord in list(self.cells.keys()):
            if coord.startswith(deleted_column):
                affected_nodes.extend(self.dag.remove_node(coord))
                
        updates = []
        
        for node in affected_nodes:
            cell = self.cells.get(node)
            if cell and cell.is_formula:
                # Substitui a velha Ref por #REF! para gerar panic no evaluate
                new_formula = re.sub(fr"\b{deleted_column}\d+\b", "#REF!", cell.raw_content)
                cell.raw_content = new_formula
                cell.value = "#REF!"
                updates.append((node, new_formula))
                
        return updates

    def evaluate_all(self) -> Dict[str, str]:
        """
        Avalia todas as células da tabela após a resolução da DAG.
        Converte as fórmulas em valores matemáticos.
        Retorna o dicionário de Resultados.
        """
        updates = {}
        
        def resolve_value(coord: str, visited: Set[str]) -> float | str:
            cell = self.cells.get(coord)
            if not cell:
                return 0.0
                
            if cell.value is not None:
                if str(cell.value) in ["#REF!", "#CIRCULAR_REF!", "#ERROR!", "#DIV/0!"]:
                    updates[coord] = str(cell.value)
                    return cell.value
                try:
                    val = float(cell.value)
                    updates[coord] = str(val)
                    return val
                except ValueError:
                    updates[coord] = "0.0"
                    return 0.0

            if not cell.is_formula:
                try:
                    cell.value = float(cell.raw_content)
                except ValueError:
                    cell.value = 0.0
                updates[coord] = str(cell.value)
                return cell.value
                
            # É Fórmula. Previne loop recursivo
            if coord in visited:
                cell.value = "#CIRCULAR_REF!"
                return cell.value
                
            visited.add(coord)
            
            formula_str = cell.raw_content[1:] # Tira o '='
            
            # Para cada referencia (Ex: A1), resolve recursivamente
            def replace_ref(match):
                ref_coord = match.group(1)
                val = resolve_value(ref_coord, visited)
                if isinstance(val, str) and val in ["#REF!", "#CIRCULAR_REF!", "#ERROR!"]:
                    raise ValueError(val) # Aborta a Regex imediatamente c/ o código do erro
                return str(val) if not isinstance(val, str) else val

            try:
                # Resolve ranges before normal references
                def replace_range(match):
                    range_str = match.group(0)
                    expanded = self._parse_range(range_str)
                    vals = [str(resolve_value(c, visited)) for c in expanded]
                    # Converts A1:A3 to [10.0, 20.0, 30.0] for the function
                    return "[" + ", ".join(vals) + "]"
                
                resolved_ranges = re.sub(r"([A-Z]+\d+:[A-Z]+\d+)", replace_range, formula_str)
                resolved_formula = re.sub(r"([A-Z]+\d+)", replace_ref, resolved_ranges)
                
                # Injeta FUNÇÕES permitidas na avaliação
                safe_locals = {**self.ALLOWED_FUNCTIONS}
                cell.value = float(eval(resolved_formula, {"__builtins__": {}}, safe_locals))
            except ValueError as ve:
                err_code = str(ve)
                if err_code in ["#REF!", "#CIRCULAR_REF!", "#ERROR!"]:
                    cell.value = err_code
                else:
                    cell.value = "#ERROR!"
            except ZeroDivisionError:
                 cell.value = "#DIV/0!"
            except Exception:
                 cell.value = "#ERROR!"
                 
            updates[coord] = str(cell.value)
            return cell.value

        for coord in self.cells.keys():
             resolve_value(coord, set())
             
        return updates
