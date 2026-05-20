import re
from typing import Any

INR_PATTERN = re.compile(r"₹\s?(\d+(?:[.,]\d{1,2})?)", re.IGNORECASE)
ALT_INR_PATTERN = re.compile(r"Rs\.?\s?(\d+(?:[.,]\d{1,2})?)", re.IGNORECASE)

RETAILER_HOST_HINTS: dict[str, str] = {
    "blinkit.com": "blinkit",
    "zepto.com": "zepto",
    "zeptonow.com": "zepto",
    "bigbasket.com": "bigbasket",
    "swiggy.com": "instamart",
}


def parse_inr(text: str) -> float | None:
    if not text:
        return None
    for pattern in (INR_PATTERN, ALT_INR_PATTERN):
        match = pattern.search(text)
        if match:
            raw = match.group(1).replace(",", "")
            try:
                return float(raw)
            except ValueError:
                continue
    return None


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
    title = (
        struct.get("title")
        or struct.get("name")
        or struct.get("product_name")
        or ""
    )
    pack_size = struct.get("packSize") or struct.get("pack_size") or struct.get("size") or ""
    # Website-schema docs use `link`; structured docs use `productUrl`/`product_url`/`uri`
    product_url = (
        struct.get("link")
        or struct.get("productUrl")
        or struct.get("product_url")
        or struct.get("uri")
        or ""
    )
    image_url = struct.get("imageUrl") or struct.get("image_url") or ""

    price = struct.get("priceInr") or struct.get("price_inr") or struct.get("price")
    if price is not None:
        try:
            final_price = float(price)
        except (TypeError, ValueError):
            final_price = None
    else:
        final_price = None

    crawled_at = struct.get("crawledAt") or struct.get("crawled_at")

    return {
        "title": str(title) if title else "",
        "packSize": str(pack_size) if pack_size else "",
        "productUrl": str(product_url) if product_url else "",
        "imageUrl": str(image_url) if image_url else "",
        "finalPriceInr": final_price,
        "crawledAt": str(crawled_at) if crawled_at else None,
        "retailer": infer_retailer(
            str(product_url) if product_url else None,
            struct,
            str(title) if title else "",
        ),
    }


def struct_to_dict(struct_data: Any) -> dict[str, Any]:
    if struct_data is None:
        return {}
    if isinstance(struct_data, dict):
        return struct_data
    if hasattr(struct_data, "items"):
        return dict(struct_data)
    return {}
