import pytest

from xadrez_das_lendas.asset_catalog import PIECE_ASSETS, piece_asset
from xadrez_das_lendas.paths import validate_assets


def test_all_catalogued_piece_assets_exist():
    assert validate_assets(set(PIECE_ASSETS.values())) == []


def test_catalog_resolves_variants_and_rejects_unknown_visual():
    assert piece_asset("torre", "branca", 2) == "torre branca_2.jpeg"
    assert piece_asset("peao", "preta", 8) == "peão_preto 8.jpeg"
    with pytest.raises(ValueError, match="Visual de peça inexistente"):
        piece_asset("rei", "branca", 2)
