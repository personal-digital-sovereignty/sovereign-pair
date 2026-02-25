import logging
import warnings
import requests
import re
from typing import Optional
from ddgs import DDGS
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Constants (could be imported from config, but keeping it simple or injecting it)
MAX_WEB_SEARCH_RESULTS = 5

def scrape_url_text(url: str, max_chars: int = 3500) -> str:
    """Busca o html da página real para obter contexto profundo (tabelas, textos longos)."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Remove scripts e estilos
            for script in soup(["script", "style"]):
                script.extract()
            # Pega o texto limpo
            text = soup.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            return text[:max_chars]
        return ""
    except Exception as e:
        logger.debug(f"Falha no scraper em {url}: {e}")
        return ""

def search_web(query: str, timelimit: Optional[str] = None) -> str:
    """
    Busca informações na internet usando DuckDuckGo (ddgs).
    Ativada manualmente pelo usuário com o comando /web.
    
    Filtros avançados habilitados:
    - region='br-pt': Prioriza resultados em PT-BR
    - safesearch='off': Sem filtro (conteúdo técnico não é unsafe)
    
    Args:
        query: Consulta de busca
        timelimit: Filtro temporal ('d'=dia, 'w'=semana, 'm'=mês, 'y'=ano)
        
    Returns:
        str: Resultados formatados ou mensagem de erro
    """
    try:
        from config import MAX_WEB_SEARCH_RESULTS as CONFIG_MAX_RESULTS
        max_results = CONFIG_MAX_RESULTS
    except ImportError:
        max_results = MAX_WEB_SEARCH_RESULTS

    try:
        time_labels = {'d': 'últimas 24h', 'w': 'última semana', 'm': 'último mês', 'y': 'último ano'}
        time_info = f" ({time_labels[timelimit]})" if timelimit and timelimit in time_labels else ""
        logger.info(f"🌐 Buscando na web: {query}{time_info}")
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ddgs = DDGS()
            results = list(ddgs.text(
                query,
                region='br-pt',
                safesearch='off',
                timelimit=timelimit,
                max_results=max_results,
            ))
        
        if not results:
            return "Nenhum resultado encontrado na busca web."
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            href = result.get('href', '')
            body = result.get('body', 'Sem descrição')
            
            # Scrape deep content for the top 2 results to allow AI to read inner tables and long texts
            if i <= 2 and href:
                deep_text = scrape_url_text(href)
                if deep_text and len(deep_text) > 200:
                    body = f"{body}\n\n   --- Extração Profunda da Página ---\n   \"{deep_text}...\""
                    
            formatted_results.append(
                f"{i}. **{result.get('title', 'Sem título')}**\n"
                f"   {body}\n"
                f"   🌐 {href}"
            )
        
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"❌ Erro na busca web: {e}")
        return f"Erro ao buscar na internet: {str(e)}"
