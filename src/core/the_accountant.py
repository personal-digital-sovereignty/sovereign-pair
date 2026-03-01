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
        if node in self.adjacency_list:
            del self.adjacency_list[node]
        if node in self.reverse_adj:
            for source in self.reverse_adj[node]:
                if source in self.adjacency_list and node in self.adjacency_list[source]:
                    self.adjacency_list[source].remove(node)
            del self.reverse_adj[node]
            
        return affected

    def detect_cycle(self, start_node: str, visited: Set[str] = None, stack: Set[str] = None) -> bool:
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
