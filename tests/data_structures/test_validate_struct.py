from __future__ import annotations

import pytest

from src.glyphser.data_structures.validate_struct import (
    validate_checkpoint_header,
    validate_trace_iter_record,
)


def test_validate_trace_iter_record_accepts_dict():
    validate_trace_iter_record({})


def test_validate_trace_iter_record_rejects_non_dict():
    with pytest.raises(TypeError):
        validate_trace_iter_record([])


def test_validate_checkpoint_header_accepts_dict():
    validate_checkpoint_header({})


def test_validate_checkpoint_header_rejects_non_dict():
    with pytest.raises(TypeError):
        validate_checkpoint_header("bad")
