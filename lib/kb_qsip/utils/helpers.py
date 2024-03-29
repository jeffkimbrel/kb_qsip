"""General helper functions for kb_qsip."""

from typing import Any

from combinatrix.converter import convert_data
from combinatrix.fetcher import DataFetcher
from pandas import DataFrame
from rpy2.robjects.packages import data, importr

qsip2 = importr("qSIP2")
qsip2_data = data(qsip2)

PARAM_NAMES = ["source", "sample", "feature"]


def retrieve_object_dataframes(
    params: dict[str, Any], qsip_config: dict[str, Any], token: str
) -> dict[str, DataFrame]:
    """Retrieve the sample, source, and feature data from the KBase workspace and convert them to dataframes.

    :param params: param dictionary from app input
    :type params: dict[str, Any]
    :param qsip_config: qsip config
    :type qsip_config: dict[str, Any]
    :param token: KBase token
    :type token: str
    :raises KeyError: _description_
    :raises RuntimeError: _description_
    :return: dictionary of dataframes keyed by KBase object ID
    :rtype: dict[str, DataFrame]
    """
    # 'source_data': "72832/2/1",
    # 'sample_data': "72832/3/1",
    # 'feature_data': "72832/7/1",
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
    converted_data = convert_data(fetched_data)

    # these can all be converted into dataframes

    dataframes: dict[str, DataFrame] = {}
    for ref in converted_data:
        dataframes[ref] = DataFrame(converted_data[ref]["dict_list"])

    return dataframes


# source data
def get_source_df(params, ws_client):

    if "debug" in params and params["debug"]:
        source_df = qsip2_data.fetch("example_source_df")["example_source_df"]

        # AJ... make df (either csv in scratch, or pandas df) from KBasesets.Sampleset
        ref = get_object_by_ref(params["source_data"], ws_client)
        # print(ref)
        # converted = convert_samples(ref)
        # print(converted)

    else:
        # get logic to import via kbase api
        pass

    return source_df


def make_source_object(source_df, params):

    # validation checks are all run inside qSIP2 R package
    source_data = qsip2.qsip_source_data(
        source_df,
        isotope=params["M_isotope"],
        source_mat_id=params["M_source_mat_id"],
        isotopolog=params["M_isotopolog"],
    )

    return source_data


# sample data
def get_sample_df(params):

    if "debug" in params and params["debug"]:
        sample_df = qsip2_data.fetch("example_sample_df")["example_sample_df"]

        # AJ... make df (either csv in scratch, or pandas df) from KBasesets.Sampleset
    else:
        # get logic to import via kbase api
        pass

    return sample_df


def make_sample_object(sample_df, params):

    if params["calculate_gradient_pos_rel_amt"]:

        # If relative amounts are not already calculated, then do this now
        sample_df = qsip2.add_gradient_pos_rel_amt(
            sample_df,
            source_mat_id=params["S_source_mat_id"],
            amt=params["S_gradient_pos_rel_amt"],
        )

        # set the params to the newly generated column
        params["S_gradient_pos_rel_amt"] = "gradient_pos_rel_amt"

    # validation checks are all run inside qSIP2 R package
    sample_data = qsip2.qsip_sample_data(
        sample_df,
        sample_id=params["S_sample_id"],
        source_mat_id=params["S_source_mat_id"],
        gradient_position=params["S_gradient_position"],
        gradient_pos_density=params["S_gradient_pos_density"],
        gradient_pos_amt=params["S_gradient_pos_amt"],
        gradient_pos_rel_amt=params["S_gradient_pos_rel_amt"],
    )

    return sample_data


# feature data
def get_feature_df(params):

    if "debug" in params and params["debug"]:
        feature_df = qsip2_data.fetch("example_feature_df")["example_feature_df"]

        # AJ... make df (either csv in scratch, or pandas df) from KBaseMatrices.AmpliconMatrix

    else:
        # get logic to import via kbase api
        pass

    return feature_df


def make_feature_object(feature_df, params):

    # validation checks are all run inside qSIP2 R package
    feature_data = qsip2.qsip_feature_data(
        feature_df, feature_id=params["F_feature_ids"], type=params["F_type"]
    )

    return feature_data


# qsip object
def make_qsip_object(source_data, sample_data, feature_data):

    # validation checks are all run inside qSIP2 R package
    return qsip2.qsip_data(source_data, sample_data, feature_data)
