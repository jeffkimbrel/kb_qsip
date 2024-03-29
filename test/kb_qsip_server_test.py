"""Main impl file tests."""

from typing import Any

import pytest
from kb_qsip.kb_qsipImpl import kb_qsip

PARAMS = {
    "workspace_name": "some_workspace_name",
    "debug": True,
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


def test_run_kb_qsip(qsip_app: kb_qsip, context: dict[str, Any]) -> None:
    """Basic run test."""
    output = qsip_app.run_kb_qsip(context, PARAMS)
    assert output == {}
