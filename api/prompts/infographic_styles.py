"""
Infographic style library. Keep IDs in sync with frontend options.
"""

STYLE_LIBRARY = {
    "lab_manual_pop": """=== STYLE: LAB MANUAL + POP EXPERIMENT ===
- Background: grayish-white with faint blueprint grid texture (#F2F2F2)
- Systemic base: muted teal/sage (#B8D8BE) for major blocks
- High-alert accent: fluorescent pink (#E91E63) only for critical warning or winner
- Marker highlights: vivid lemon yellow (#FFF200) as translucent highlight
- Line art: ultra-fine charcoal brown (#2D2926) for grids and coordinates
- High density: 6-7 modules minimum, minimal margins, add tiny metadata (timestamps, barcodes)
- Technical diagrams: exploded views, cross-sections, coordinate rulers, hairline grids
- Typography: bold brutalist headers, tiny technical annotations (8pt look)
- Avoid cute icons, avoid flat stock vectors, avoid empty white space
""",
    "blueprint_pop_lab": """=== STYLE: BLUEPRINT POP LAB ===
- Background: grayish-white with faint blueprint grid texture (#F2F2F2)
- Systemic base: muted teal/sage (#B8D8BE) for major blocks
- High-alert accent: fluorescent pink (#E91E63) only for critical warning or winner
- Marker highlights: vivid lemon yellow (#FFF200) as translucent highlight
- Line art: ultra-fine charcoal brown (#2D2926) for grids and coordinates
- Information as coordinates: every module has coordinate labels (R-20, G-02, SEC-08)
- Lab manual aesthetic: mix micro technical drawings with large data headers
- High density: 6-7 modules minimum, minimal margins, add tiny metadata (timestamps, barcodes)
- Technical diagrams: exploded views, cross-sections, coordinate rulers, hairline grids
- Data blocks: slight offset “marker-over-print” highlight effect
- Symbols: cross-hair targets, Σ/Δ/∞, directional arrows (X/Y axis)
- Typography: bold brutalist headers + tiny technical annotations (8pt look)
- Avoid cute icons, avoid flat stock vectors, avoid empty white space
""",
    "executive_clean": """=== STYLE: EXECUTIVE CLEAN ===
- Background: warm off-white (#F7F4EF) with very subtle paper texture
- Palette: charcoal (#1F2328), deep green (#2D5A3D), muted gold accent (#C9A65C)
- Layout: strong hierarchy, generous grid, clear modular cards
- Visuals: crisp icons, thin separators, high legibility
- Typography: bold serif or neo-grotesk headers, clean body text
- Density: high, but readable; avoid clutter
""",
    "editorial_cards": """=== STYLE: EDITORIAL CARD GRID ===
- Background: light ivory (#F6F1E9)
- Palette: soft pastel blocks with one deep accent
- Layout: multi-card grid, each card has title + short phrase
- Visuals: simple line icons, subtle shadows, consistent spacing
- Typography: bold headline + compact body
- Density: medium-high with strong scan-ability
""",
}

DEFAULT_STYLE_ID = "executive_clean"
