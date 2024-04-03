"""General helper functions for kb_qsip."""

import logging
from typing import Any

from combinatrix.converter import convert_data
from combinatrix.fetcher import DataFetcher
from pandas import DataFrame
from rpy2.robjects.methods import RS4
from rpy2.robjects.packages import PackageData, data, importr
from rpy2.robjects import rl

qsip2 = importr("qSIP2")
baseR = importr('base')
dplyr = importr('dplyr')

PARAM_NAMES = ["source", "sample", "feature"]


def retrieve_convert_objects(
    params: dict[str, Any], qsip_config: dict[str, Any], token: str
) -> dict[str, Any]:
    """Retrieve the sample, source, and feature data from the KBase workspace.

    :param params: param dictionary from app input
    :type params: dict[str, Any]
    :param qsip_config: qsip config
    :type qsip_config: dict[str, Any]
    :param token: KBase token
    :type token: str
    :return: dictionary of datasets for each object, keyed by KBase ID
    :rtype: dict[str, Any]
    """
    fetcher = DataFetcher(qsip_config, {"token": token})
    to_fetch = set()
    for src in PARAM_NAMES:
        upa = params.get(f"{src}_data")
        if not upa:
            err_msg = f"{src}_data parameter not found!"
            raise ValueError(err_msg)

        to_fetch.add(upa)

    if len(to_fetch) != len(PARAM_NAMES):
        err_msg = f"Only found {len(to_fetch)} unique KBase objects to fetch. Check your parameters and rerun the app."
        raise ValueError(err_msg)

    fetched_data = fetcher.fetch_objects_by_ref(list(to_fetch))
    return convert_data(fetched_data)


def retrieve_object_dataframes_from_qsip2_data(
    params: dict[str, Any]
) -> dict[str, RS4]:
    """Retrieve sample data from the R qsip2 package and save it as a dataframe."""
    qsip2_data: PackageData = data(qsip2)
    dataframes: dict[str, RS4] = {}
    for src in PARAM_NAMES:
        # get the UPA of the input data
        upa = params.get(f"{src}_data")
        # retrieve the corresponding data from qsip2_data and save it to a dictionary
        dataframes[upa] = qsip2_data.fetch(f"example_{src}_df")[f"example_{src}_df"]

    return dataframes


def make_source_object(source_df: DataFrame | RS4, params: dict[str, Any]) -> RS4:

    # validation checks are all run inside qSIP2 R package

    source_df = dplyr.select(source_df, rl('-save_date'))

    # de-MISIPify if necessary
    source_df = qsip2.remove_isotopolog_label_check(source_df)

    return qsip2.qsip_source_data(
        source_df,
        isotope=params["M_isotope"],
        source_mat_id="name",
        isotopolog=params["M_isotopolog"],
    )

def make_sample_object(sample_df: DataFrame | RS4, params: dict[str, Any]) -> RS4:

    sample_df = dplyr.select(sample_df, rl('-save_date'))

    if params["calculate_gradient_pos_rel_amt"] == 1:

        # If relative amounts are not already calculated, then do this now
        sample_df = qsip2.add_gradient_pos_rel_amt(
            sample_df,
            source_mat_id=params["S_source_mat_id"],
            amt=params["S_gradient_pos_rel_amt"],
        )

        # set the params to the newly generated column
        params["S_gradient_pos_rel_amt"] = "gradient_pos_rel_amt"

    # validation checks are all run inside qSIP2 R package
    return qsip2.qsip_sample_data(
        sample_df,
        sample_id="name",
        source_mat_id=params["S_source_mat_id"],
        gradient_position=params["S_gradient_position"],
        gradient_pos_density=params["S_gradient_pos_density"],
        gradient_pos_amt=params["S_gradient_pos_amt"],
        gradient_pos_rel_amt=params["S_gradient_pos_rel_amt"],
    )


# feature data
def make_feature_object(feature_df: DataFrame | RS4, params: dict[str, Any]) -> RS4:

    # print(baseR.dim(feature_df))
    # print(baseR.colnames(feature_df))
    
    feature_df = qsip2.pivot_kbase_amplicon_matrix(feature_df)

    # print(baseR.dim(feature_df))
    # print(baseR.colnames(feature_df))

    # validation checks are all run inside qSIP2 R package
    return qsip2.qsip_feature_data(
        feature_df, feature_id="row_id", type=params["F_type"]
    )


# qsip object
def make_qsip_object(
    dataframes: dict[str, DataFrame | RS4],
    params: dict[str, Any],
) -> RS4:

    source_data = make_source_object(dataframes[params["source_data"]], params) 
    # logging.info(source_data)

    sample_data = make_sample_object(dataframes[params["sample_data"]], params)
    # logging.info(sample_data)

    feature_data = make_feature_object(dataframes[params["feature_data"]], params)
    # logging.info(feature_data)

    # validation checks are all run inside qSIP2 R package
    return qsip2.qsip_data(source_data, sample_data, feature_data)
