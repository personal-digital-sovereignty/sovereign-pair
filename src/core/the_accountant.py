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
        Retorna lista de dependentes que vão quebrar e virar `#REF!`.
        """
        affected = list(self.adjacency_list.get(node, []))
        # Limpa os elos
        self.adjacency_list.pop(node, None)
        if node in self.reverse_adj:
            for source in self.reverse_adj[node]:
                if source in self.adjacency_list and node in self.adjacency_list[source]:
                    self.adjacency_list[source].remove(node)
            self.reverse_adj.pop(node, None)
            
        return affected

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
        Converte 'A1:A3' para ['A1', 'A2', 'A3']
        """
        match = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", range_str)
        if not match:
            return [range_str]
            
        start_col, start_row = match.group(1), int(match.group(2))
        end_col, end_row = match.group(3), int(match.group(4))
        
        # TODO: Implementação avançada de conversão Base26 p/ Base10 (Letras p/ Num)
        # Para Range horizontal B1:D1 etc
        
        cells = []
        for r in range(start_row, end_row + 1):
            cells.append(f"{start_col}{r}")
            
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

    def handle_cell_deletion(self, deleted_coordinate: str) -> List[Tuple[str, str]]:
        """
        Quando uma Coluna inteira é apagada e o Front Notifica:
        Identifica todo mundo que dependia dessa coord e converte para #REF!
        Retorna a lista de celulas a atualizar no arquivo.
        """
        affected_nodes = self.dag.remove_node(deleted_coordinate)
        updates = []
        
        for node in affected_nodes:
            cell = self.cells.get(node)
            if cell and cell.is_formula:
                # Substitui a velha Ref por #REF! para gerar panic no evaluate
                new_formula = re.sub(fr"\b{deleted_coordinate}\b", "#REF!", cell.raw_content)
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
                if str(cell.value) in ["#REF!", "#CIRCULAR_REF!", "#ERROR!"]:
                    return cell.value
                try:
                    return float(cell.value)
                except ValueError:
                    return 0.0

            if not cell.is_formula:
                try:
                    cell.value = float(cell.raw_content)
                except ValueError:
                    cell.value = 0.0
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
                return str(val) if not isinstance(val, str) or val not in ["#REF!", "#CIRCULAR_REF!", "#ERROR!"] else '0' # Ignorar quebra na mat, let root fail

            # Isso varre A1, B2 e substitui pelos números reais.
            resolved_formula = re.sub(r"([A-Z]+\d+)", replace_ref, formula_str)
            
            # Verifica se herdou algum erro nas dependencias imediatas
            # Simples proxy para #REF!
            if any(str(resolve_value(ref, set())) in ["#REF!", "#CIRCULAR_REF!"] for ref in self.dag.reverse_adj.get(coord, [])):
                 cell.value = "#REF!"
                 updates[coord] = str(cell.value)
                 return cell.value

            try:
                # Usar EVAL puro apenas para escopo numérico restrito provisório
                # Fase 17 restringe entrada via tipTap a números e operações básicas.
                # A implementação real de The Accountant usará `ast.parse` e caminhada na AST Tree.
                cell.value = float(eval(resolved_formula, {"__builtins__": {}}, {}))
            except ZeroDivisionError:
                 cell.value = "#DIV/0!"
            except Exception:
                 cell.value = "#ERROR!"
                 
            updates[coord] = str(cell.value)
            return cell.value

        for coord in self.cells.keys():
             resolve_value(coord, set())
             
        return updates
