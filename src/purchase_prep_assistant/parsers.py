"""URL and identifier parsing utilities.

These functions deliberately avoid network access. They do not resolve Amazon
short links, scrape pages, or inspect checkout flows.
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

ASIN_RE = re.compile(r"^[A-Z0-9]{10}$")
ASIN_IN_PATH_RE = re.compile(r"/(?:dp|gp/product|product|ASIN)/([A-Z0-9]{10})(?:[/?#]|$)")
ALLOWED_AMAZON_HOSTS = {
    "amazon.co.jp",
    "www.amazon.co.jp",
    "amazon.com",
    "www.amazon.com",
    "amzn.asia",
    "www.amzn.asia",
}
CHECKOUT_PATH_MARKERS = (
    "/checkout",
    "/gp/buy",
    "/gp/cart",
    "/cart",
    "/buy/spc",
    "/payselect",
    "/gp/address",
)


def normalize_host(host: str | None) -> str:
    """Return a lowercase hostname without a trailing dot."""
    return (host or "").lower().rstrip(".")


def extract_asin_from_amazon_url(url: str) -> str | None:
    """Extract an ASIN from common Amazon product URL patterns.

    Amazon short links such as https://amzn.asia/d/... are intentionally not
    resolved, because resolving them would require network access and may cross
    into page automation or tracking behavior. In that case this function
    returns None and the generated checklist asks for manual confirmation.
    """
    parsed = urlparse(url)
    path_match = ASIN_IN_PATH_RE.search(parsed.path)
    if path_match:
        return path_match.group(1)

    query = parse_qs(parsed.query)
    for key in ("asin", "ASIN", "itemId", "itemid"):
        candidates = query.get(key, [])
        for candidate in candidates:
            if ASIN_RE.fullmatch(candidate):
                return candidate
    return None


def is_allowed_amazon_product_url(url: str) -> bool:
    """Return True for Amazon product/reference URLs that are not checkout URLs."""
    parsed = urlparse(url)
    host = normalize_host(parsed.hostname)
    if parsed.scheme not in {"http", "https"}:
        return False
    if host not in ALLOWED_AMAZON_HOSTS:
        return False
    path = parsed.path.lower()
    return not any(marker in path for marker in CHECKOUT_PATH_MARKERS)


def describe_url(url: str) -> dict[str, str | bool | None]:
    """Return a compact, serializable description of a submitted URL."""
    parsed = urlparse(url)
    return {
        "host": normalize_host(parsed.hostname),
        "path": parsed.path,
        "allowed_product_reference": is_allowed_amazon_product_url(url),
        "asin": extract_asin_from_amazon_url(url),
    }
