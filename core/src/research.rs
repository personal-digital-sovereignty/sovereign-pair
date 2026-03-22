use reqwest::Client;
use scraper::{Html, Selector};
use std::time::Duration;
use regex::Regex;

/// Arquitetura nativa do Sovereign Web-Augmented Generation (WAG)
/// Blindada via Rust para injetar contexto externo ao RAG Cíbrido.
pub struct DeepResearchEngine {
    client: Client,
}

impl DeepResearchEngine {
    pub fn new() -> Self {
        let client = Client::builder()
            .timeout(Duration::from_secs(15))
            .user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
            .build()
            .unwrap_or_else(|_| Client::new());

        Self { client }
    }

    /// Realiza a varredura e o scrape profundo da URL alvo.
    pub async fn scrape_url(&self, url: &str) -> Result<String, String> {
        let response = self.client.get(url).send().await.map_err(|e| format!("HTTP Request failed: {}", e))?;
        
        if !response.status().is_success() {
            return Err(format!("Server returned HTTP {}", response.status()));
        }

        let html_content = response.text().await.map_err(|e| format!("Failed to read HTML body: {}", e))?;
        
        Ok(self.sanitize_to_markdown(&html_content))
    }

    /// Limpa o HTML ruidoso (scripts, estilos, anúncios) e extrai o texto principal em formato Semântico (Markdown-like).
    fn sanitize_to_markdown(&self, html: &str) -> String {
        let document = Html::parse_document(html);
        
        // Remove tags ofensores (Anti-Junk)
        // Isso é uma filtragem em memória antes da decodificação.
        let mut text_blocks = Vec::new();
        
        // Vamos capturar parágrafos, cabeçalhos e listas
        let selector = Selector::parse("p, h1, h2, h3, h4, li, article, main, .content").unwrap();
        
        for element in document.select(&selector) {
            let tag_name = element.value().name();
            
            // Foca o inner text, ignorando scripts implícitos
            let inner_text = element.text().collect::<Vec<_>>().join(" ");
            let clean_text = inner_text.trim();
            
            if clean_text.is_empty() {
                continue;
            }
            
            // Formata o header
            let formatted = match tag_name {
                "h1" => format!("# {}\n", clean_text),
                "h2" => format!("## {}\n", clean_text),
                "h3" => format!("### {}\n", clean_text),
                "h4" => format!("#### {}\n", clean_text),
                "li" => format!("- {}", clean_text),
                _ => format!("{}\n", clean_text), // <p>, <article>, <main>
            };
            
            text_blocks.push(formatted);
        }
        
        // Retira blocos curtos demais ou inúteis
        let mut markdown = text_blocks.join("\n");
        
        // Expressão Regular agressiva para remover espaçamentos múltiplos (Whitespace Normalization)
        let re = Regex::new(r"\n{3,}").unwrap();
        markdown = re.replace_all(&markdown, "\n\n").to_string();
        
        markdown
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_html_to_markdown_sanitization() {
        let engine = DeepResearchEngine::new();
        let html_mock = r#"
            <!DOCTYPE html>
            <html>
            <head>
                <script>alert("HACKED");</script>
                <style>body { color: red; }</style>
            </head>
            <body>
                <header>Ignored Header Navigation</header>
                <main>
                    <h1>Sovereign Pair WAG Test</h1>
                    <p>This is a test paragraph describing the Deep Research module.</p>
                    <ul>
                        <li>Item 1</li>
                        <li>Item 2</li>
                    </ul>
                </main>
                <aside>Adverts here</aside>
            </body>
            </html>
        "#;

        let markdown = engine.sanitize_to_markdown(html_mock);
        
        // Asserting the inclusion of valid semantic elements
        assert!(markdown.contains("# Sovereign Pair WAG Test"));
        assert!(markdown.contains("This is a test paragraph"));
        assert!(markdown.contains("- Item 1"));
        
        // Asserting the EXCLUSION of malicious/junk elements
        assert!(!markdown.contains("HACKED"), "Scraper leaked raw Script text!");
        assert!(!markdown.contains("body { color: red; }"), "Scraper leaked raw CSS text!");
        assert!(!markdown.contains("Ignored Header Navigation"), "Scraper leaked <header> navigation!");
        assert!(!markdown.contains("Adverts here"), "Scraper leaked <aside> tags!");
    }
}
