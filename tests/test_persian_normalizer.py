from etl.normalizers import normalize_fa


def test_normalize_fa_unifies_common_variants() -> None:
    assert normalize_fa("  دانشگاهِ‌ زنجان  ") == "دانشگاه زنجان"
    assert normalize_fa("دانشگاه يک") == "دانشگاه یک"
