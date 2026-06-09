"""Riprendi una listing già creata applicando i passi mancanti del payload.

Usato come fallback quando create_listing.py fallisce a metà (es. su
set_inventory): la listing esiste già con immagini+video, ma mancano
varianti e traduzioni.

Uso:
    python3 finish_listing.py <listing_id> <payload.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from etsy import (  # noqa: E402
    EtsyError, load_config, set_inventory, set_translation,
    set_variation_translation,
)


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("Uso: finish_listing.py <listing_id> <payload.json>")
    listing_id = int(sys.argv[1])
    payload = json.loads(Path(sys.argv[2]).read_text())
    cfg = load_config()
    shop_id = cfg["shop_id"]

    variations = payload.get("variations")
    if variations:
        print(f"→ set_inventory ({len(variations['options'])} opzioni)")
        set_inventory(listing_id, variations=variations)

    vt_map = payload.get("variation_translations") or {}
    if variations and vt_map:
        prop_id = variations.get("property_id", 513)
        for lang, vt in vt_map.items():
            print(f"→ variation translation [{lang}]: {vt['property_name']}")
            try:
                set_variation_translation(
                    shop_id, listing_id, prop_id, lang,
                    property_name=vt["property_name"], values=vt["values"],
                )
            except EtsyError as e:
                print(f"  ! {lang} fallita: {e}")

    for lang, t in (payload.get("translations") or {}).items():
        print(f"→ translation [{lang}]: {t['title'][:60]}…")
        try:
            set_translation(shop_id, listing_id, lang,
                            title=t["title"], description=t["description"],
                            tags=t.get("tags"))
        except EtsyError as e:
            print(f"  ! {lang} fallita: {e}")

    print(f"\n✓ Listing {listing_id} completata")


if __name__ == "__main__":
    main()
