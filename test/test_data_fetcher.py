"""Tests for the data fetching code."""

import logging
from test.conftest import AMP, INVALID_DATA_FETCHER_PARAMS, SSA, SSB, TEST_UPA, paramify
from test.conftest import body_match_vcr as vcr
from typing import Any

import pytest
from combinatrix.constants import DATA, INFO
from combinatrix.fetcher import DataFetcher

# enable extra vcrpy logging for troubleshooting purposes
#logging.basicConfig()
# vcr_log = logging.getLogger("vcr")
# vcr_log.setLevel(logging.DEBUG)


@pytest.mark.parametrize("param", INVALID_DATA_FETCHER_PARAMS)
def test_init(param: list[Any]) -> None:
    """Test that initialisation fails if params are not supplied."""
    with pytest.raises(
        ValueError,
        match="'config.kbase-endpoint' and 'context.token' are required by the DataFetcher",
    ):
        DataFetcher(*param)


@pytest.mark.parametrize(
    "param",
    paramify(
        [
            {
                "ref_list": [TEST_UPA["INVALID_A"], TEST_UPA["INVALID_B"]],
                "missing": f"{TEST_UPA['INVALID_A']}, {TEST_UPA['INVALID_B']}",
                "id": "all_missing",
            },
            {
                "ref_list": [TEST_UPA["INVALID_A"], TEST_UPA[AMP]],
                "missing": TEST_UPA["INVALID_A"],
                "id": "one_missing",
            },
        ]
    ),
)
def test_fetch_objects_by_ref_missing_items(
    param: dict[str, Any], data_fetcher: DataFetcher
) -> None:
    """Check that missing refs are reported correctly."""
    with vcr.use_cassette(
        f"test/data/cassettes/{param['id']}.yaml",
    ), pytest.raises(
        ValueError,
        match=f"The following KBase objects could not be retrieved: {param['missing']}",
    ):
        data_fetcher.fetch_objects_by_ref(param["ref_list"])


@pytest.mark.parametrize(
    "param",
    paramify(
        [
            {
                "ref_list": [TEST_UPA[AMP]],
                "sample_data_expected": [],
                "id": "no_sampleset",
            },
            {
                "ref_list": [TEST_UPA[SSA]],
                "sample_data_expected": [TEST_UPA[SSA]],
                "id": "single_sampleset",
            },
            {
                "ref_list": [
                    TEST_UPA[AMP],
                    TEST_UPA[SSA],
                    TEST_UPA[SSB],
                ],
                "sample_data_expected": [
                    TEST_UPA[SSA],
                    TEST_UPA[SSB],
                ],
                "id": "multi_sampleset",
            },
        ]
    ),
)
def test_fetch_objects_by_ref_with_samples(
    param: dict[str, Any], data_fetcher: DataFetcher
) -> None:
    """Ensure that samples are fetched from the sampleset."""
    with vcr.use_cassette(
        f"test/data/cassettes/{param['id']}.yaml",
    ):
        output = data_fetcher.fetch_objects_by_ref(param["ref_list"])

    for ref in param["ref_list"]:
        assert ref in output
        assert INFO in output[ref]
        assert DATA in output[ref]
        if ref in param["sample_data_expected"]:
            assert output[ref][INFO]["type"] == "KBaseSets.SampleSet-2.0"
            assert (
                str(len(output[ref][DATA]["sample_data"]))
                == output[ref][INFO]["meta"]["num_samples"]
            )
            assert "sample_data" in output[ref][DATA]
            assert {item["id"] for item in output[ref][DATA]["samples"]} == {
                item["id"] for item in output[ref][DATA]["sample_data"]
            }
        else:
            assert "sample_data" not in output[ref][DATA]
