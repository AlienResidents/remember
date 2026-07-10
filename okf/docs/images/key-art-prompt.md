---
type: Documentation
description: "REMEMBER — Key Art Image Prompt"
resource: docs/images/key-art-prompt.md
timestamp: 2026-07-10T16:49:18Z
---

# key-art-prompt

Source path: `docs/images/key-art-prompt.md`

## Content

# REMEMBER — Key Art Image Prompt

Prompt for a frontier image-generation model to produce key/hero art for the
REMEMBER project. The prompt is anchored on the *actual* visual language already
established in `server/webui/styles.css` and the inline logo SVG in
`server/webui/index.html` — same palette, same logo geometry, same motifs — so
the output reads as native artwork rather than a generic sci-fi cover.

## Theme summary (for reference)

- **Name / meaning:** REMEMBER = Recursive Enhanced Memory by Enhanced Recall.
  Shared, team-scoped memory layer for AI coding agent sessions.
- **Palette:** bg `#0a0e17` / `#111827`; neon cyan `#00f5ff`, purple `#b400ff`,
  blue `#0066ff`, pink `#ff006e`, green `#00ff88`; text `#e5e7eb`.
- **Typography:** Nulshock Bd (geometric sci-fi display) for headings;
  Science Gothic for body. Cyan→purple gradient wordmark with cyan glow.
- **Motifs:** animated cyan grid floor, rising cyan particles, concentric-ring
  logo with diamond + glowing core, glassmorphic dark panels with cyan borders
  and glow, unicode geometric glyphs (⌕ ◈ ◉ ◇ + ⊘ ✗).

## Prompt

> A sci-fi themed key art illustration for "REMEMBER," a shared team memory
> system for AI coding agents. Dark cyberpunk/synthwave command-console
> aesthetic.
>
> **Composition:** A central holographic "memory core" — concentric glowing
> rings (an outer cyan ring and an inner purple ring) rotating around a
> diamond/rhombus with a bright cyan glowing sphere at its center, suggesting a
> data vault or neural archive. The core floats above a vast perspective grid
> floor of cyan lines receding into dark blue-black space (Tron-style grid, 50px
> squares). Behind it, a deep starfield gradient from #0a0e17 at the edges to a
> subtle purple-blue nebula glow at the center.
>
> **Palette (exact):** Background near-black blue-black #0a0e17 and #111827.
> Primary neon cyan #00f5ff. Secondary neon purple #b400ff. Accent neon pink
> #ff006e and neon green #00ff88. Text/foreground light grey #e5e7eb. Glowing
> neon edges and volumetric cyan light bloom.
>
> **Surrounding the core:** Glassmorphic translucent dark panels
> (semi-transparent #111827 at ~80% opacity with thin cyan borders at ~20%
> alpha and cyan glow) arranged in orbit — each panel faintly showing abstract
> memory fragments: markdown documents, code snippets, vector embeddings
> visualized as constellations of dots, and connection lines linking related
> memories. The panels suggest a browsable archive of collective team knowledge.
>
> **Mood:** Holographic, luminous, high-tech but clean and readable — not grimy
> street-cyberpunk. Sense of depth, calm precision, an authoritative memory
> archive that an AI assistant would consult. Sacred-geometry meets
> data-center.
>
> **Typography area:** Reserve clean negative space at the top or bottom for the
> wordmark "REMEMBER" in a geometric sci-fi display font (like Nulshock),
> rendered with a cyan-to-purple gradient fill and a cyan glow. Subtitle below
> it reads "Recursive Enhanced Memory by Enhanced Recall" in a lighter,
> spaced-out sans-serif. Keep text crisp and legible.
>
> **Style:** Digital art, ultra-detailed, cinematic lighting, subtle film
> grain, 16:9 or square aspect, suitable as project hero/key art. No
> photorealistic humans, no chrome, no lens flare overload — restrained,
> elegant neon-on-dark. Geometric, symbolic, architectural.

## Notes

- Aspect ratio and whether the image model renders text are left as choices.
  Many frontier image models render text poorly — if yours is unreliable,
  drop the **Typography area** paragraph and instead request a clean text-safe
  negative-space zone so the wordmark can be composited in post.
- The prompt mirrors the inline logo SVG (concentric rings + diamond + glowing
  core). If a separate canonical logo asset exists, point the model at it for
  tighter fidelity.
