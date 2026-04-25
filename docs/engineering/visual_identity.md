# 🎨 Identidade Visual & Design System
## O Estilo "Modern Enterprise" (Neural Architect)

Este documento define os padrões estéticos do Sovereign Pair. Nosso objetivo é criar uma interface que pareça uma ferramenta de alta engenharia, inspirada em painéis de telemetria aeroespacial e terminais de IA de ponta.

---

## 1. Princípios Fundamentais

1. **Aesthetics over Generics**: Fuja do "Bootstrap feel". Use cores saturadas em tons de ardósia, tipografia editorial e espaçamentos generosos.
2. **Data-Rich but Not Cluttered**: Alta densidade de informação (telemetria), mas com hierarquia clara via tipografia e cores de superfície.
3. **The Glass Immersion**: Use Glassmorphism (backdrop-blur) para elementos transientes como modais e dropdowns.
4. **No-Line Rule**: Evite bordas de 1px para separar seções. Use mudanças sutis na cor de fundo (Tonal Shifts) para criar profundidade natural.

---

## 2. Paleta de Cores (Dark Mode Primário)

O Sovereign Pair utiliza um sistema de cores baseado em tons de **Slate & Azure**, otimizado para longas sessões de trabalho sem fadiga ocular.

- **Fundo (Surface)**: `#0c111d` (Deep Space Blue).
- **Contêineres (Surface Containers)**: 
    - `Low`: `#131a2a` (Base das seções).
    - `High`: `#1d253b` (Cards e elementos ativos).
- **Acentos (Primary)**: `#74b0ff` (Azure Glow). Usado para CTAs e indicadores de estado ativo.
- **Texto**: 
    - `On Surface`: `#f3f4f6` (Off-white para leitura).
    - `Variant`: `#9ca3af` (Cinza para metadados e descrições).

---

## 3. Tipografia Editorial

Combinamos duas fontes para equilibrar o visual técnico com a clareza editorial:

- **Manrope (Headlines)**: Usada para títulos de seções e status de alto nível. Evoca autoridade e modernidade.
- **Inter (UI Elements)**: Usada para todo o corpo de texto, inputs e dados. É a fonte de trabalho que garante legibilidade máxima.

---

## 4. Componentes e Interações

### Botões e CTAs
- **Primário**: Gradiente linear de `#74b0ff` para `#5ea3f8` com bordas arredondadas `md` (6px).
- **Ghost**: Apenas texto com hover de brilho sutil.

### Cards de Telemetria
- Devem usar `surface_container_low` com um raio de borda `lg` (12px).
- A separação deve ser feita via **Espaço em Branco** (escala de 16px ou 20px), nunca por linhas divisórias sólidas.

### Modais e Flyouts
- Aplicar `backdrop-blur: 20px` e opacidade de 70% na cor da superfície para criar o efeito de vidro.
- Sombra: `0px 24px 48px -12px rgba(0, 0, 0, 0.5)` (Sombra ambiente suave).

---

## 5. Regras de Ouro (Do's and Don'ts)

✅ **FAÇA**:
- Use gradientes sutis em indicadores de progresso.
- Mantenha < 5% da tela com cores de acento vibrantes.
- Use pesos de fonte (Medium/SemiBold) para criar hierarquia, em vez de tamanhos gigantes.

❌ **NÃO FAÇA**:
- Não use preto puro (`#000000`) como fundo principal.
- Não use sombras pesadas e escuras em elementos pequenos.
- Não use bordas sólidas de alto contraste; opte pelo "Ghost Border" (contorno com 10-20% de opacidade).
