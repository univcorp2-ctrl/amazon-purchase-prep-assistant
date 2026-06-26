from purchase_prep_assistant.parsers import (
    describe_url,
    extract_asin_from_amazon_url,
    is_allowed_amazon_product_url,
)


def test_extract_asin_from_dp_url() -> None:
    assert extract_asin_from_amazon_url("https://www.amazon.co.jp/dp/B012345678") == "B012345678"


def test_short_link_is_allowed_but_not_resolved() -> None:
    url = "https://amzn.asia/d/0a7kZ6KA"
    assert is_allowed_amazon_product_url(url)
    assert extract_asin_from_amazon_url(url) is None


def test_checkout_url_is_rejected() -> None:
    assert not is_allowed_amazon_product_url(
        "https://www.amazon.co.jp/gp/buy/spc/handlers/display.html"
    )


def test_describe_url() -> None:
    description = describe_url("https://www.amazon.co.jp/gp/product/B012345678")
    assert description["allowed_product_reference"] is True
    assert description["asin"] == "B012345678"
