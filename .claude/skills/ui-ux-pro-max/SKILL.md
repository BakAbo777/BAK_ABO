# UI/UX Pro Max — Design Intelligence Toolkit

AI-powered design database: 67 UI styles, 161 color palettes, 57 font pairings, 99 UX guidelines, 25 chart types, 15+ tech stacks.

**Install location:** `.claude/skills/ui-ux-pro-max/`
**Search script:** `python .claude/skills/ui-ux-pro-max/scripts/search.py`

---

## When to use

Invoke when the user needs:
- UI style recommendation for any page or component
- Color palette for ecommerce / fashion / editorial
- Font pairing with Google Fonts import
- UX guidelines checklist (accessibility, mobile, conversion)
- Design system generation for a product

---

## Search commands

```bash
# Full design system (recommended starting point)
python .claude/skills/ui-ux-pro-max/scripts/search.py "<product> <keywords>" --design-system -p "ProjectName"

# Style only
python .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain style -n 5

# Color palette
python .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain color -n 3

# Typography
python .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain typography -n 3

# UX guidelines
python .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain ux -n 5

# For Shopify/ecommerce (Liquid/CSS stack)
python .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --stack html-tailwind
```

## Available domains
`style` | `color` | `typography` | `landing` | `ux` | `chart` | `product`

## Available stacks
`html-tailwind` | `react` | `nextjs` | `astro` | `vue` | `svelte` | `shadcn`

---

## BakAbo / BKS — recommended query

```bash
python .claude/skills/ui-ux-pro-max/scripts/search.py "fashion ecommerce editorial AI-art luxury minimal" --design-system -p "BakAbo BKS"
```

This returns: pattern, style, colors, typography, key effects, anti-patterns.

Always cross-reference results with `bakabo-design-system` tokens before applying — BKS uses its own canonical color system.
