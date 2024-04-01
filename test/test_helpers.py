"""Tests for the helper functions."""

from __future__ import annotations

from test.conftest import INVALID_DATA_FETCHER_PARAMS, paramify
from typing import Any

import pytest
from kb_qsip.utils.helpers import retrieve_object_dataframes


@pytest.mark.parametrize(
    "params",
    paramify(
        [
            {"input": {}, "missing": "source", "id": "empty_dict"},
            {"input": {"source_data": None}, "missing": "source", "id": "source_None"},
            {
                "input": {"source_data": ""},
                "missing": "source",
                "id": "source_empty_string",
            },
            {
                "input": {"source_data": "this", "sample_data": "that"},
                "missing": "feature",
                "id": "feature_omitted",
            },
            {
                "input": {
                    "source_data": "this",
                    "sample_data": "that",
                    "feature_data": None,
                },
                "missing": "feature",
                "id": "feature_None",
            },
            {
                "input": {"feature_data": "this", "sample_data": "that"},
                "missing": "source",
                "id": "source_omitted",
            },
        ]
    ),
)
def test_retrieve_object_dataframes_fail(
    params: dict[str, Any], config: dict[str, Any]
) -> None:
    """Ensure that all params are present."""
    with pytest.raises(
        ValueError, match=f"{params['missing']}_data parameter not found!"
    ):
        retrieve_object_dataframes(params["input"], config, "token")


@pytest.mark.parametrize(
    "params",
    paramify(
        [
            {
                "input": {
                    "source_data": "123/4/5",
                    "sample_data": "123/4/5",
                    "feature_data": "123/4/5",
                },
                "n_found": 1,
                "id": "one_found",
            },
            {
                "input": {
                    "source_data": "123/4/5",
                    "sample_data": "123/4/5",
                    "feature_data": "678/9/0",
                },
                "n_found": 2,
                "id": "two_found",
            },
        ]
    ),
)
def test_retrieve_object_dataframes_unique_fail(
    params: dict[str, Any], config: dict[str, Any]
) -> None:
    """Ensure that all params are present."""
    with pytest.raises(
        ValueError,
        match=f"Only found {params['n_found']} unique KBase objects to fetch. Check your parameters and rerun the app.",
    ):
        retrieve_object_dataframes(params["input"], config, "token")
