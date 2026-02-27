"""Canonical CBOR vector tests."""

from .vector_loader import load_vectors
from src.glyphser.serialization.canonical_cbor import encode_canonical_hex


def test_canonical_cbor_vectors():
    data = load_vectors()
    for vector in data["vectors"]:
        actual = encode_canonical_hex(vector["input_json"])
        assert actual == vector["expected_cbor_hex"], vector["id"]
