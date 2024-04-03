"""General helper functions for kb_qsip."""

import logging
import os
from typing import Any

from combinatrix.converter import convert_data
from combinatrix.fetcher import DataFetcher
from pandas import DataFrame
import rpy2.robjects as robjects
from rpy2.robjects.methods import RS4
from rpy2.robjects.packages import PackageData, data, importr
from rpy2.robjects import rl
from rpy2.robjects import pandas2ri
from rpy2.robjects.lib import ggplot2

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


def run_feature_filter(qsip_object: RS4, params: dict[str, Any]) -> RS4:
    qsip_object = qsip2.run_feature_filter(qsip_object,
                   unlabeled_source_mat_ids = qsip2.get_all_by_isotope(qsip_object, rl("'16O'")),
                   labeled_source_mat_ids = qsip2.get_all_by_isotope(qsip_object, rl("'18O'")),
                   min_unlabeled_sources = 1,
                   min_labeled_sources = 1,
                   min_unlabeled_fractions = 1,
                   min_labeled_fractions = 1)
    
    return qsip_object

def run_resampling(qsip_object: RS4, params: dict[str, Any]) -> RS4:

    # TODO verify params["resamples"] is an int

    qsip_object = qsip2.run_resampling(qsip_object,
                                       resamples = params["resamples"],
                                        with_seed = 14,
                                        allow_failures = True,
                                        progress = False)
    
    return qsip_object

def run_EAF_calculations(qsip_object: RS4, params: dict[str, Any]) -> RS4:
    qsip_object = qsip2.run_EAF_calculations(qsip_object)
    
    return qsip_object

def summarize_EAF_values(qsip_object: RS4, params: dict[str, Any]) -> DataFrame:
    # TODO verify params["confidence"] is a float between 0-1

    eaf_summary = qsip2.summarize_EAF_values(qsip_object, 
                                             confidence = params["confidence"])
    
    with (robjects.default_converter + pandas2ri.converter).context():
        pd_EAF_summary = robjects.conversion.get_conversion().rpy2py(eaf_summary)

    return(pd_EAF_summary)
    
def write_EAF_summary(eaf_summary: DataFrame, output_directory: str):

    eaf_summary.to_csv(os.path.join(output_directory, "EAF_summary.txt"), sep="\t", index=False)


def plot_source_wads(qsip_object: RS4, output_directory: str, params: dict[str, Any]):

    # for some reason the columns have been converted to lower case
    qsip_plot = qsip2.plot_source_wads(qsip_object, 
                           group = params["groups"].lower()) 
    robjects.r.ggsave(filename=os.path.join(output_directory, "source_wads.png"), 
                    plot=qsip_plot, 
                    width=80, 
                    height=40, 
                    unit='mm')
    
def plot_filter_results(qsip_object: RS4, output_directory: str):

    qsip_plot = qsip2.plot_filter_gradient_position(qsip_object)

    robjects.r.ggsave(filename=os.path.join(output_directory, "filter_results.png"), 
                    plot=qsip_plot, 
                    width=300, 
                    height=150, 
                    unit='mm')