"""Main impl file tests."""

from typing import Any

from kb_qsip.kb_qsipImpl import kb_qsip

PARAMS = {
    "workspace_name": "some_workspace_name",
    "debug": False,
    # data files
    "source_data": "73223/2/1",
    "sample_data": "73223/3/3",
    "feature_data": "73223/8/1",
    # "M" denotes source_data
    "M_isotope": "isotope",
    #"M_source_mat_id": "name",
    "M_isotopolog": "isotopolog",
    # "S" denotes sample_data
    #"S_sample_id": "name",
    "S_source_mat_id": "source_mat_id",
    "S_gradient_position": "gradient_position",
    "S_gradient_pos_density": "gradient_pos_density",
    "S_gradient_pos_amt": "qpcr.16s.copies.g.soil",
    "calculate_gradient_pos_rel_amt": False,
    "S_gradient_pos_rel_amt": "gradient_pos_rel_amt",
    # "F" denotes feature_data
    #"F_feature_ids": "row_id",
    "F_type": "relative",
    # Analysis
    "resamples": 1000,
    "resample_success": 0.8,
    "confidence": 0.9,
}


def test_run_kb_qsip(config: dict[str, Any], context: dict[str, Any]) -> None:
    """Basic run test."""
    qsip_app = kb_qsip(config)
    output = qsip_app.run_kb_qsip(context, PARAMS)
    assert output == {}
