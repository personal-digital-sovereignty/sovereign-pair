# Design System: The Cognitive Workspace

## 1. Overview & Creative North Star: "The Informed Curator"
In an era of AI-driven noise, the "Modern Enterprise" RAG (Retrieval-Augmented Generation) Command Center must act as a filter, not a firehose. This design system is built upon the **Creative North Star: The Informed Curator.** 

The goal is to move beyond the "SaaS-dashboard-in-a-box" aesthetic. We achieve this through **Editorial Precision**—using high-contrast typography scales and intentional asymmetry. Instead of rigid, boxed-in grids, we use expansive breathing room and tonal layering to guide the user’s eye through complex data. The result is a UI that feels like a premium intelligence report: authoritative, calm, and impeccably organized.

---

## 2. Colors: Tonal Architecture
We avoid the "flatness" of standard enterprise software by using a sophisticated palette of off-whites and cool grays, punctuated by high-chroma intent colors.

### The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders to define sections. Traditional lines create visual "clutter" that fatigues the user. Boundaries must be defined through background color shifts. For example, a `surface-container-low` (#f3f4f5) side panel sitting against a `surface` (#f8f9fa) main stage.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers of fine paper.
- **Base Layer:** `surface` (#f8f9fa)
- **Secondary Workspace:** `surface-container-low` (#f3f4f5)
- **Active Cards/Modals:** `surface-container-lowest` (#ffffff)
- **Deep Content/Search Bars:** `surface-container-high` (#e7e8e9)

### The "Glass & Gradient" Rule
To add "soul" to the enterprise experience, use Glassmorphism for floating elements (like command palettes or hover-state tooltips). Use a `surface-container-lowest` color at 70% opacity with a `20px` backdrop-blur. 

**Signature Texture:** For primary CTAs or AI "Generating" states, use a subtle linear gradient from `primary` (#001360) to `primary-container` (#002395) at a 135-degree angle. This adds a tactile, metallic depth that flat hex codes cannot replicate.

---

## 3. Typography: Editorial Authority
We pair the utilitarian precision of **Inter** with the structural elegance of **Manrope** for headlines. This creates a "New York Times meets Silicon Valley" aesthetic.

- **Display & Headlines (Manrope):** Use these to anchor the page. The large scale (`display-lg` at 3.5rem) should be used sparingly to define major modules.
- **Body & Labels (Inter):** High legibility for data-dense RAG outputs. 
- **The Hierarchy Strategy:** Always lead with a strong `headline-sm` (#191c1d) followed by a `body-md` in `on-surface-variant` (#444653). This contrast in weight and color ensures the user can scan the "Command Center" quickly without reading every word.

---

## 4. Elevation & Depth: Tonal Layering
Depth is achieved through "stacking" rather than traditional drop shadows.

- **The Layering Principle:** To lift a card, do not reach for a shadow first. Place a `surface-container-lowest` (#ffffff) card on top of a `surface-container-low` (#f3f4f5) background. The 2% shift in brightness is enough for the human eye to perceive depth without adding visual "weight."
- **Ambient Shadows:** For "Global Actions" (floating buttons), use an ultra-diffused shadow: `offset: 0 12px, blur: 32px, color: rgba(25, 28, 29, 0.06)`. Note the use of the `on-surface` color for the shadow tint; never use pure black.
- **The "Ghost Border" Fallback:** If a container holds extremely similar data types, use a "Ghost Border": `outline-variant` (#c5c5d5) at **15% opacity**. It should be felt, not seen.

---

## 5. Components: Minimalist Utility

### Buttons & Actions
- **Primary:** Gradient-filled (`primary` to `primary-container`), `md` (0.375rem) corner radius. Use `primary-fixed` (#dee1ff) for hover states.
- **Secondary:** Transparent background with a "Ghost Border."
- **Lateral Sidebar:** A permanent `surface-container-low` fixture. Icons should be `on-surface-variant` (#444653), shifting to `primary` (#001360) only when active.

### Cards & Data Lists
- **The "No Divider" Mandate:** Forbid the use of horizontal rules (`<hr>`). Separate list items using `spacing-4` (0.9rem) or a subtle background toggle between `surface` and `surface-container-lowest`.
- **RAG Status Badges:** Use `tertiary-container` (#003d1c) with `on-tertiary-fixed-variant` (#005228) for "Source Verified" badges. The high contrast ensures trust.
- **Data-Dense Charts:** Use `px` (1px) stroke widths for axes. Use `secondary` (#50606f) for grid lines, but at 20% opacity.

### Input & Search (The Command Bar)
- **The AI Input:** Use `surface-container-lowest`, a `xl` (0.75rem) corner radius, and a `primary` (#001360) "Ghost Border" to signify the RAG system is ready for a prompt.

---

## 6. Do’s and Don’ts

### Do
- **Do** use `spacing-10` (2.25rem) or larger for outer page margins to create an "Editorial" feel.
- **Do** use `tertiary` (Emerald) for AI confidence scores and `error` (Crimson) for halluncination alerts.
- **Do** use `surface-dim` (#d9dadb) for inactive or "disabled" card states to keep the palette cohesive.

### Don’t
- **Don’t** use pure black (#000000) for text. Always use `on-surface` (#191c1d) to maintain the "Professional Light" aesthetic.
- **Don’t** use rounded corners larger than `xl` (0.75rem) for functional containers; excessive roundness feels "consumer-app" rather than "enterprise-grade."
- **Don’t** use traditional "Blue" for links within AI-generated text. Use `primary` (#001360) with a medium-weight underline to signify a clickable source/citation.