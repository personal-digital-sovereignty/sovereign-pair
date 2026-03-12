import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def parse_document_to_markdown(filepath: str) -> str:
    """
    Roteador Universal Dinâmico. Consome Arquivos Nativos O.S (Binários ou Texto) e devolve representações seguras em Markdown.
    Blinda o App de UnicodeDecodeErrors perigosos acossando o FileSystem Web.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo O.S não localizado no Handler: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == ".pdf":
        return _parse_pdf(filepath)
    elif ext in [".docx", ".odt", ".epub", ".rtf", ".pptx"]:
        return _parse_pandoc(filepath)
    else:
        # Fallback para Textos Planos O.S ou Código Fonte
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            return f"> [!WARNING]\n> **Bloqueio O.S (Codificação)**\n>\n> O arquivo `{os.path.basename(filepath)}` (Formato {ext}) é denso ou possui uma codificação não-suportada textualmente (Não é UTF-8). A proteção de Memória barrou a Leitura."

def _parse_pdf(filepath: str) -> str:
    try:
        import pymupdf4llm
        md_text = pymupdf4llm.to_markdown(filepath)
        filename = os.path.basename(filepath)
        
        # Adicionando um aviso de somete-leitura no TOPO do markdown gerado para PDFs
        header = f"> [!NOTE]\n> **Pre-Renderização Dinâmica PDF:** Extração Textual Estrutural feita on-the-fly (`MuPdf Engine`). Edições visuais na UI não compilarão fisicamente como novo PDF de volta_.\n\n"
        md_text = header + md_text
        return md_text
    except ImportError:
         logger.warning("pymupdf4llm not installed.")
         return "> [!error]\n> **Erro Sistêmico O.S - Dependência Ausente**\n>\n> O pacote extrator `pymupdf4llm` não opera no Kernel Python Local. Não é possível renderizar PDFs dinamicamente para a View."
    except Exception as e:
         return f"> [!error]\n> **Deformação PDF Header (MuPdf)**\n>\n> O Motor colapsou tentando fatiar este documento: {str(e)}"

def _parse_pandoc(filepath: str) -> str:
    try:
        import pypandoc
        
        # pandoc extrai direto para markdown puro c/ suporte ODT e DOCX
        output = pypandoc.convert_file(filepath, 'markdown')
        filename = os.path.basename(filepath)
        
        header = f"> [!NOTE]\n> **Decompilação O.S On-The-Fly (Pandoc Engine)**\n> Conversor Oficial engoliu o binário '{filename}' para leitura Markdown.\n\n"
        return header + output
        
    except ImportError:
         return "> [!error]\n> **Erro Sistêmico O.S - Módulo Pypandoc Não Engatado**\n>\n> O invólucro web `pypandoc` não pôde ser injetado. Rodar `pip install pypandoc-binary`."
    except Exception as e:
         return f"> [!error]\n> **Motor Pandoc Cedeu (Binary Error)**\n>\n> Não fomos capazes de desempacotar: {str(e)}\n>\n> *Nota O.S: Pandoc falha radicalmente contra arquivos corrompidos ou salvos com criptografia O.S nativa bloqueada.*"
