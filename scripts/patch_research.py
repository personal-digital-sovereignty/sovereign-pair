with open("core/src/research.rs", "r", encoding="utf-8") as f:
    content = f.read()

target = "pub async fn scrape_url(&self, original_url: &str) -> Result<String, String> {\n        let mut url = original_url.to_string();"
replacement = """pub async fn scrape_url(&self, original_url: &str) -> Result<String, String> {
        if !crate::guardrails::is_safe_url(original_url) {
            return Err("SSRF Guardrail Ativado: O domínio de destino não é roteável publicamente.".to_string());
        }
        let mut url = original_url.to_string();"""

content = content.replace(target, replacement)

with open("core/src/research.rs", "w", encoding="utf-8") as f:
    f.write(content)
