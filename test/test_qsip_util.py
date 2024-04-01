"""Tests of the QsipUtil class."""

from test.conftest import PARAMS_BASE
from test.conftest import body_match_vcr as vcr
from typing import Any

from kb_qsip.utils.qsip_util import QsipUtil
from rpy2.robjects.methods import RS4


def test_run_debug(config: dict[str, Any], context: dict[str, Any]) -> None:
    """Test running QsipUtil with debug data."""
    qsip_util = QsipUtil(config, context)
    debug_params = {**PARAMS_BASE, "debug": True}
    output = qsip_util.run(debug_params)
    assert isinstance(output, RS4)
    # add in some more tests here


def test_run_appdev_samples(config: dict[str, Any], context: dict[str, Any]) -> None:
    """Run the qsip2 tool with data from appdev."""
    qsip_util = QsipUtil(config, context)

    # use a pre-recorded response to avoid having to hit the server when running tests
    with vcr.use_cassette(
        "test/data/cassettes/test_run.yaml",
    ):
        test_data = {
            "sample_data": "72724/19/1",
            "source_data": "72724/21/1",
            "feature_data": "72724/23/1",
        }
        output = qsip_util.run({**PARAMS_BASE, **test_data})
        assert isinstance(output, RS4)
        # add in more tests here
