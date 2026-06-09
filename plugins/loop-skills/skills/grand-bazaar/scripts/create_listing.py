"""Create a draft Etsy listing from a JSON payload (+ image/video upload).

Usage:
    python3 create_listing.py path/to/listing.json
    python3 create_listing.py -    # legge il JSON da stdin

Payload minimo: vedi references/listing.example.json dello skill.

Tutti i campi che mancano e hanno un default sensibile vengono presi da
config.json. Lo stato della listing creata è sempre "draft".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from etsy import (  # noqa: E402
    EtsyError, api, load_config, set_inventory, set_translation,
    set_variation_translation, upload_image, upload_video,
)

VALID_WHO_MADE = {"i_did", "someone_else", "collective"}
VALID_WHEN_MADE = {
    "made_to_order", "2020_2026", "2020_2025", "2010_2019", "2006_2009",
    "before_2006", "2000_2005", "1990s", "1980s", "1970s", "1960s",
    "1950s", "1940s", "1930s", "1920s", "1910s", "1900s", "1800s",
    "1700s", "before_1700",
}


def _require(payload: dict, key: str) -> object:
    if key not in payload or payload[key] in (None, ""):
        raise EtsyError(f"Campo obbligatorio mancante: {key}")
    return payload[key]


def create_listing(payload: dict) -> dict:
    cfg = load_config()
    shop_id = cfg.get("shop_id")
    if not shop_id:
        raise EtsyError("shop_id non in config.json — esegui prima get_shop_info.py")

    who_made = payload.get("who_made", "i_did")
    when_made = payload.get("when_made", "made_to_order")
    if who_made not in VALID_WHO_MADE:
        raise EtsyError(f"who_made non valido: {who_made} (usa uno di {sorted(VALID_WHO_MADE)})")
    if when_made not in VALID_WHEN_MADE:
        raise EtsyError(f"when_made non valido: {when_made}")

    title = str(_require(payload, "title"))[:140]
    description = str(_require(payload, "description"))
    price = float(_require(payload, "price"))
    variations_count = len(payload.get("variations", {}).get("options", [])) if payload.get("variations") else 0
    quantity = int(payload.get("quantity") or max(1, variations_count))
    taxonomy_id = int(_require(payload, "taxonomy_id"))

    tags = payload.get("tags") or []
    materials = payload.get("materials") or []
    if len(tags) > 13:
        raise EtsyError("Max 13 tag")
    if any(len(t) > 20 for t in tags):
        raise EtsyError("Ogni tag max 20 caratteri")
    if len(materials) > 13:
        raise EtsyError("Max 13 materiali")

    form = {
        "quantity": quantity,
        "title": title,
        "description": description,
        "price": f"{price:.2f}",
        "who_made": who_made,
        "when_made": when_made,
        "taxonomy_id": taxonomy_id,
        "is_supply": "true" if payload.get("is_supply", False) else "false",
        "state": "draft",
    }
    shipping_profile_id = payload.get("shipping_profile_id") or cfg.get("default_shipping_profile_id")
    if shipping_profile_id:
        form["shipping_profile_id"] = shipping_profile_id
    shop_section_id = payload.get("shop_section_id") or cfg.get("default_shop_section_id")
    if shop_section_id:
        form["shop_section_id"] = shop_section_id
    return_policy_id = payload.get("return_policy_id") or cfg.get("default_return_policy_id")
    if return_policy_id:
        form["return_policy_id"] = return_policy_id
    readiness_state_id = payload.get("readiness_state_id") or cfg.get("default_readiness_state_id")
    if readiness_state_id:
        form["readiness_state_id"] = readiness_state_id
    if tags:
        form["tags"] = ",".join(tags)
    if materials:
        form["materials"] = ",".join(materials)

    listing = api("POST", f"/shops/{shop_id}/listings", form=form)
    listing_id = listing["listing_id"]
    print(f"✓ Listing draft creata: id={listing_id}")
    print(f"  URL admin: https://www.etsy.com/your/shops/me/tools/listings/{listing_id}")

    image_paths = payload.get("image_paths") or []
    for i, path_str in enumerate(image_paths, start=1):
        p = Path(path_str).expanduser()
        if not p.exists():
            print(f"  ! immagine non trovata: {p}")
            continue
        print(f"  → upload immagine {i}/{len(image_paths)}: {p.name}")
        upload_image(shop_id, listing_id, p, rank=i)

    video_path = payload.get("video_path")
    if video_path:
        v = Path(video_path).expanduser()
        if not v.exists():
            print(f"  ! video non trovato: {v}")
        else:
            print(f"  → upload video: {v.name}")
            try:
                upload_video(shop_id, listing_id, v, name=title)
            except EtsyError as e:
                print(f"  ! upload video fallito: {e}")

    variations = payload.get("variations")
    if variations:
        print(f"  → impostando varianti ({len(variations.get('options', []))} opzioni)…")
        set_inventory(listing_id, variations=variations)

    variation_translations = payload.get("variation_translations") or {}
    if variations and variation_translations:
        prop_id = variations.get("property_id", 513)
        for lang, vt in variation_translations.items():
            print(f"  → traduzione varianti [{lang}]: {vt.get('property_name')}")
            try:
                set_variation_translation(
                    shop_id, listing_id, prop_id, lang,
                    property_name=vt["property_name"], values=vt["values"],
                )
            except EtsyError as e:
                print(f"  ! traduzione varianti {lang} fallita: {e}")

    translations = payload.get("translations") or {}
    for lang, t in translations.items():
        print(f"  → traduzione [{lang}]: {t.get('title', '')[:60]}…")
        try:
            set_translation(
                shop_id, listing_id, lang,
                title=t["title"], description=t["description"],
                tags=t.get("tags"),
            )
        except EtsyError as e:
            print(f"  ! traduzione {lang} fallita: {e}")

    return listing


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Uso: create_listing.py <listing.json | ->")
    arg = sys.argv[1]
    raw = sys.stdin.read() if arg == "-" else Path(arg).read_text()
    payload = json.loads(raw)
    listing = create_listing(payload)
    print(json.dumps({"listing_id": listing["listing_id"], "state": listing.get("state")}, indent=2))


if __name__ == "__main__":
    main()
