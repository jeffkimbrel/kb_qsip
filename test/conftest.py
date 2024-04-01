"""Fixtures and global settings for the tests."""

from __future__ import annotations

import json
import os
import shutil
from configparser import ConfigParser
from test import TEST_BASE_DIR
from typing import TYPE_CHECKING, Any

import pytest
import vcr
from combinatrix.constants import DATA, DL, FN, KEYS
from combinatrix.fetcher import DataFetcher

from lib.kb_qsip.kb_qsipImpl import kb_qsip

if TYPE_CHECKING:
    from collections.abc import Callable

CONFIG_FILE = os.environ.get(
    "KB_DEPLOYMENT_CONFIG", os.path.join(TEST_BASE_DIR, "./deploy.cfg")
)

TOKEN = os.environ.get("KB_AUTH_TOKEN", "fake_token")
SDK_CALLBACK_URL = os.environ.get("SDK_CALLBACK_URL")

TEST_DATA = {
    "source_data": "72832/2/1",
    "sample_data": "72832/3/1",
    "feature_data": "72832/7/1",
}

# These refs are all on prod.
TEST_UPA = {
    "SAMPLESET_A": "72724/4/1",
    "SAMPLESET_B": "72724/5/1",
    "AMPLICON": "72724/11/1",
    "INVALID_A": "1/2/3",
    "INVALID_B": "4/5/6",
}


PARAMS_BASE = {
    "workspace_id": "some_workspace_id",
    # data files
    "source_data": "72832/2/1",
    "sample_data": "72832/3/1",
    "feature_data": "72832/7/1",
    # "M" denotes source_data
    "M_isotope": "Isotope",
    "M_source_mat_id": "source",
    "M_isotopolog": "isotopolog",
    # "S" denotes sample_data
    "S_sample_id": "sample",
    "S_source_mat_id": "source",
    "S_gradient_position": "Fraction",
    "S_gradient_pos_density": "density_g_ml",
    "S_gradient_pos_amt": "avg_16S_g_soil",
    "calculate_gradient_pos_rel_amt": True,
    "S_gradient_pos_rel_amt": "avg_16S_g_soil",
    # "F" denotes feature_data
    "F_feature_ids": "ASV",
    "F_type": "counts",
    # Analysis
    "resamples": 1000,
    "resample_success": 0.8,
    "confidence": 0.9,
}


INVALID_DATA_FETCHER_PARAMS = [
    pytest.param([None, None], id="two_nones"),
    pytest.param([{}, {}], id="two_empty_dicts"),
    pytest.param([{"kbase-endpoint": "whatever"}, {"token": None}], id="no_token"),
    pytest.param([{"kbase-endpoint": "whatever"}, {"token": ""}], id="empty_token"),
    pytest.param([{"kbase-endpoint": None}, {"token": "whatever"}], id="no_endpt"),
    pytest.param([{"kbase-endpoint": ""}, {"token": "whatever"}], id="empty_endpt"),
]

ERRORS = {
    "samples_node_tree_0": "12345/4/0: incorrect number of sample node trees for sample e2114bfa-5716-4e70-ad17-e97c35120b5a, 16O.16C",
    "samples_node_tree_multiple": "12345/6/0: incorrect number of sample node trees for sample e2114bfa-5716-4e70-ad17-e97c35120b5a, 16O.16C",
}

MATCH_ON = ["method", "scheme", "host", "port", "path", "body_matcher"]

body_match_vcr = vcr.VCR(
    record_mode="once",
    filter_headers=["authorization"],
    match_on=MATCH_ON,
    filter_post_data_parameters=["id"],
)


def body_matcher(r1, r2) -> None:
    """Compare the body contents of two requests to work out if they are identical or not."""
    r1_body = json.loads(r1.body.decode())
    r2_body = json.loads(r2.body.decode())
    if "id" in r1_body:
        del r1_body["id"]
    if "id" in r2_body:
        del r2_body["id"]
    assert r1_body == r2_body


body_match_vcr.register_matcher("body_matcher", body_matcher)


def paramify(test_params: list[dict[str, Any]]) -> list[Any]:
    """Convert a list of dictionaries into a parameter set for a test.

    If the "id" key is present, it is used as the id for the parameter.

    :param test_params: list of dictionaries
    :type test_params: list[dict[str, Any]]
    :return: list of pytest parameters
    :rtype: list[Any]
    """
    if "id" in test_params[0]:
        return [pytest.param(tp, id=tp["id"]) for tp in test_params]
    return [pytest.param(tp) for tp in test_params]


def read_json_file(file_path: str) -> dict[str, Any]:
    """Read in JSON from a stored data file.

    :param file_path: path to the file of interest
    :type file_path: str
    :return: parsed JSON data
    :rtype: dict
    """
    with open(os.path.join(TEST_BASE_DIR, DATA, file_path), encoding="utf-8") as fh:
        return json.load(fh)


# Fixture logic to load input and output based on a parameter
def load_test_case(case_name: str) -> dict[str, Any]:
    """Load the appropriate data for a test."""
    input_file = f"{case_name}.json"
    output_file = f"{case_name}_converted.json"

    result: dict[str, Any] = {"input": read_json_file(input_file)}

    if os.path.exists(os.path.join(TEST_BASE_DIR, DATA, output_file)):
        result["output"] = {}
        untyped_output = read_json_file(output_file)
        result["output"][DL] = untyped_output[DL]
        result["output"][FN] = set(untyped_output[FN])
        result["output"][KEYS] = {}
        for k in ["user", "controlled"]:
            result["output"][KEYS][k] = set(untyped_output[KEYS][k])
    if case_name in ERRORS:
        result["error"] = ERRORS[case_name]

    return result


def generate_fixture(case_name: str) -> Callable:
    """Generate fixtures for the given case name."""

    @pytest.fixture(name=case_name, scope="session")
    def fixture_func() -> dict[str, Any]:
        """Retrieve fixture data from a file."""
        return load_test_case(case_name)

    return fixture_func


# "12345/1/1": "samples_all_controlled"
# "12345/2/1": "samples_b"
# "12345/3/1": "samples_no_fields"
# "12345/4/0": "samples_node_tree_0"
# "12345/5/1": "samples_node_tree_multiple_under_node"
# "12345/6/0": "samples_node_tree_multiple"


def auto_generate_fixtures() -> None:
    """Autogenerate some data fixtures."""
    # list the fixtures to be autogenerated:
    autogen_fixtures = [
        "samples_all_controlled",
        "samples_b",
        "samples_no_fields",
        "samples_node_tree_0",
        "samples_node_tree_multiple_under_node",
        "samples_node_tree_multiple",
    ]

    # Assuming file naming convention is consistent and only input files are used to generate fixture names
    for case_name in autogen_fixtures:
        globals()[case_name] = generate_fixture(case_name)


# Call the function to auto-generate fixtures
auto_generate_fixtures()


@pytest.fixture(scope="session")
def config() -> dict[str, str]:
    """Parses the configuration file and retrieves the values under the Combinatrix header.

    :return: dictionary of key-value pairs
    :rtype: dict[str, Any]
    """
    print(f"Retrieving config from {CONFIG_FILE}")  # noqa: T201
    cfg_dict = {}
    config_parser = ConfigParser()
    config_parser.read(CONFIG_FILE)
    for nameval in config_parser.items("kb_qsip"):
        cfg_dict[nameval[0]] = nameval[1]

    if not cfg_dict.get("kbase-endpoint"):
        err_msg = "Missing required config variable 'kbase-endpoint'"
        raise RuntimeError(err_msg)

    return cfg_dict


@pytest.fixture(scope="session")
def context() -> dict[str, str]:
    """Generate the context that accompanies API requests.

    For the purposes of this app, all that's needed is an auth token.

    :return: context data structure
    :rtype: dict[str, str]
    """
    return {"token": TOKEN}


@pytest.fixture(scope="session")
def scratch_dir(config: dict[str, str]) -> str:
    """Calculate the path to the scratch directory and create it if it doesn't exist.

    :param config: config
    :type config: dict[str, str]
    :return: absolute path to the scratch directory
    :rtype: str
    """
    scratch_dir = (
        config["scratch"]
        if os.path.isabs(config["scratch"])
        else os.path.abspath(config["scratch"])
    )
    shutil.copytree(os.path.join(TEST_BASE_DIR, DATA), scratch_dir, dirs_exist_ok=True)
    return scratch_dir


@pytest.fixture(scope="session")
def data_fetcher(config: dict[str, str], context: dict[str, Any]) -> DataFetcher:
    """An instance of the DataFetcher class.

    :param config: KBase config
    :type config: dict[str, str]
    :param context: context for a KBase request
    :type context: dict[str, Any]
    :return: new DataFetcher instance
    :rtype: DataFetcher
    """
    return DataFetcher(config, context)


@pytest.fixture(scope="session")
def qsip_app(config: dict[str, Any]) -> kb_qsip:
    """Generate an instance of the kb_qsip impl app."""
    return kb_qsip(config)
