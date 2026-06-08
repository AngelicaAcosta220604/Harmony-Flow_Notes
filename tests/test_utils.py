from utils.string_utils import normalize_text, slugify

def test_normalize():
    assert normalize_text("  Привет   Мир ") == "привет мир"

def test_slugify():
    assert slugify("Привет Мир") == "privet-mir"
