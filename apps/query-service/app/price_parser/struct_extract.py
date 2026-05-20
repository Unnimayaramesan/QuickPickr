"""Document field extraction / retailer inference."""

from __future__ import annotations

from typing import Any

RETAILER_HOST_HINTS: dict[str, str] = {
    "blinkit.com": "blinkit",
    "grofers.com": "blinkit",
    "zepto.com": "zepto",
    "zeptonow.com": "zepto",
    "bigbasket.com": "bigbasket",
    "bigbasket.in": "bigbasket",
    "swiggy.com": "instamart",
}


def infer_retailer(url: str | None, struct: dict[str, Any], title: str = "") -> str | None:
    if struct.get("retailer"):
        return str(struct["retailer"]).lower()
    haystack = f"{url or ''} {title}".lower()
    if not haystack.strip():
        return None
    for host, retailer in RETAILER_HOST_HINTS.items():
        if host in haystack:
            return retailer
    name_hints = {
        "blinkit": "blinkit",
        "grofers": "blinkit",
        "zepto": "zepto",
        "bigbasket": "bigbasket",
        "instamart": "instamart",
        "swiggy": "instamart",
    }
    for needle, retailer in name_hints.items():
        if needle in haystack:
            return retailer
    return None


def extract_from_struct(struct: dict[str, Any]) -> dict[str, Any]:
    title = struct.get("title") or struct.get("name") or struct.get("product_name") or ""
    pack_size = struct.get("packSize") or struct.get("pack_size") or struct.get("size") or ""
    product_url = (
        struct.get("link")
        or struct.get("productUrl")
        or struct.get("product_url")
        or struct.get("uri")
        or ""
    )
    image_url = struct.get("imageUrl") or struct.get("image_url") or ""
    retailer = infer_retailer(str(product_url) if product_url else None, struct, str(title))

    zone_id_raw = (
        struct.get("zoneId")
        or struct.get("zone_id")
        or None
    )
    sku_id_raw = (
        struct.get("skuId")
        or struct.get("sku_id")
        or struct.get("id")
        or None
    )
    tier_raw = struct.get("freshnessTier") or struct.get("freshness_tier")

    price = (
        struct.get("priceInr")
        or struct.get("price_inr")
        or struct.get("finalPriceInr")
        or struct.get("final_price_inr")
        or struct.get("price")
    )

    fee = struct.get("deliveryFeeInr") or struct.get("delivery_fee_inr")

    final_price = None
    if price is not None:
        try:
            final_price = float(price)
        except (TypeError, ValueError):
            final_price = None

    delivery_fee_inr = None
    if fee is not None:
        try:
            delivery_fee_inr = float(fee)
        except (TypeError, ValueError):
            delivery_fee_inr = None

    crawled_at = struct.get("crawledAt") or struct.get("crawled_at")

    rf = retailer
    if rf is None and struct.get("retailer") is not None:
        rf = str(struct["retailer"]).lower()

    return {
        "title": str(title) if title else "",
        "packSize": str(pack_size) if pack_size else "",
        "productUrl": str(product_url) if product_url else "",
        "imageUrl": str(image_url) if image_url else "",
        "finalPriceInr": final_price,
        "deliveryFeeInr": delivery_fee_inr,
        "crawledAt": str(crawled_at) if crawled_at else None,
        "retailer": rf,
        "zoneId": str(zone_id_raw) if zone_id_raw else "",
        "skuId": str(sku_id_raw) if sku_id_raw else "",
        "freshnessTier": str(tier_raw) if tier_raw else "",
        "matchConfidence": "high",
        "snippetForPriceFallback": "",
    }


def struct_to_dict(struct_data: Any) -> dict[str, Any]:
    if struct_data is None:
        return {}
    if isinstance(struct_data, dict):
        return dict(struct_data)
    if hasattr(struct_data, "items"):
        try:
            return dict(struct_data)
        except TypeError:
            return {}
    return {}
