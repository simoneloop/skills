# Shop profile (personalization)

Copy this file to your data dir and fill it in:

```bash
cp "${CLAUDE_SKILL_DIR}/references/shop-profile.example.md" ~/.claude/etsy-tools/shop-profile.md
```

The `etsy-upload` skill reads `${ETSY_TOOLS_DIR:-~/.claude/etsy-tools}/shop-profile.md`
**first** and follows it for every shop-specific decision (brand voice, target
languages, terminology, price band, materials policy). It lives outside this
repo so it's never committed. Delete sections that don't apply.

---

## Shop
- **Shop name:** <e.g. MyHandmadeShop>
- **Primary language:** <e.g. it>
- **Currency:** <e.g. EUR>
- **What you sell:** <one or two lines — product category, style, what makes it distinctive>

## Target languages (translations)
List the languages every listing must be translated into (besides the primary).
Leave empty for primary-language only.
- <e.g. en, fr, es, de>

Per-keyword translation conventions (optional, keeps SEO consistent):
- "<term>" → EN `<...>`, FR `<...>`, ES `<...>`, DE `<...>`

## Brand voice & copy rules
- **Title style:** <core keywords that must always appear; SEO conventions>
- **Description structure:** <e.g. sections, symbols, what story to tell>
- **Tone:** <e.g. warm, artisanal, minimalist>
- **Always say / never say:** <terminology you require or forbid>

## Pricing
- **How to price:** <e.g. align to similar active listings; default band X–Y; never below Z>

## Materials policy
- <e.g. leave `materials` empty; or always list specific materials; never mention karats>

## Defaults
- **who_made:** <i_did | someone_else | collective>
- **when_made:** <e.g. made_to_order>
- **Typical taxonomy_ids:** <e.g. 1216 rings, 1183 necklaces>

## Variations
- <how you handle sizes/lengths/colors; cross-language option naming rules>
