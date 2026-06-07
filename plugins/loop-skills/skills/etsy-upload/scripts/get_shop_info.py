"""Discover shop_id, shipping profiles, sections, return policies.

Run after auth.py:
    python3 get_shop_info.py

Saves shop_id into config.json automatically. Prints shipping profiles,
sections, return policies — the user picks defaults and pastes their IDs
into config.json (default_shipping_profile_id, default_shop_section_id,
default_return_policy_id).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from etsy import api, load_auth, load_config, save_config  # noqa: E402


def main() -> None:
    cfg = load_config()
    auth = load_auth()
    user_id = auth["user_id"]

    try:
        me = api("GET", f"/users/{user_id}")
        print(f"Utente: {me.get('login_name')} ({me.get('primary_email')})")
    except Exception:
        pass  # richiede scope email_r, non strettamente necessario

    shops = api("GET", f"/users/{user_id}/shops")
    shop_id = shops.get("shop_id") if isinstance(shops, dict) and "shop_id" in shops else None
    if shop_id is None and isinstance(shops, dict) and "results" in shops:
        results = shops["results"]
        if results:
            shop_id = results[0]["shop_id"]
    if shop_id is None:
        sys.exit(f"Nessuno shop trovato per l'utente. Response: {shops}")

    shop = api("GET", f"/shops/{shop_id}")
    print(f"\nShop: {shop['shop_name']} (id={shop_id}, valuta={shop.get('currency_code')})")
    cfg["shop_id"] = shop_id

    print("\n— Shipping profiles —")
    profiles = api("GET", f"/shops/{shop_id}/shipping-profiles")
    for p in profiles.get("results", []):
        print(f"  id={p['shipping_profile_id']}  {p.get('title')}  (origin={p.get('origin_country_iso')})")
    if not profiles.get("results"):
        print("  (nessuno — creane uno da Etsy seller dashboard prima di pubblicare)")

    print("\n— Shop sections —")
    sections = api("GET", f"/shops/{shop_id}/sections")
    for s in sections.get("results", []):
        print(f"  id={s['shop_section_id']}  {s.get('title')}")
    if not sections.get("results"):
        print("  (nessuna)")

    print("\n— Return policies —")
    try:
        policies = api("GET", f"/shops/{shop_id}/policies/return")
        for p in policies.get("results", []):
            print(f"  id={p['return_policy_id']}  accepts_returns={p.get('accepts_returns')}  accepts_exchanges={p.get('accepts_exchanges')}")
        if not policies.get("results"):
            print("  (nessuna)")
    except Exception as e:
        print(f"  (impossibile leggere: {e})")

    save_config(cfg)
    print(f"\n✓ shop_id={shop_id} salvato in config.json")
    print("  Aggiungi manualmente in config.json:")
    print("    default_shipping_profile_id (obbligatorio per pubblicare)")
    print("    default_shop_section_id     (opzionale)")
    print("    default_return_policy_id    (obbligatorio se la shop ha policy attive)")


if __name__ == "__main__":
    main()
