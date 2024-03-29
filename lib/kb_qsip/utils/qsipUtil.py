"""Main kb_qsip code."""

import datetime
import logging
import os
from typing import Any

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.WorkspaceClient import Workspace
from rpy2.robjects.packages import data, importr

from kb_qsip.utils import helpers


class qsipUtil:

    def __init__(
        self: "qsipUtil", config: dict[str, Any], context: dict[str, Any]
    ) -> None:
        self.config = config
        self.context = context
        self.token: str = context.get("token", "")
        self.callback_url = config.get("callback_url", "")
        if not self.token:
            err_msg = "Auth token required to access workspace data"
            raise RuntimeError(err_msg)
        self.timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.kbr = KBaseReport(self.callback_url)

    def run(self: "qsipUtil", params: dict[str, Any]) -> dict[str, Any]:

        qsip2 = importr("qSIP2")
        qsip2_data = data(qsip2)
        logging.info(qsip2.__version__)

        # retrieve the data from the workspace, indexed by their KBase UPA
        dataframes_by_ref = helpers.retrieve_object_dataframes(
            params, self.config, self.token
        )

        # source data
        source_df = helpers.get_source_df(
            params, Workspace(self.config["workspace-url"], token=self.token)
        )
        source_data = helpers.make_source_object(source_df, params)
        # logging.info(source_data)

        # sample data
        sample_df = helpers.get_sample_df(params)
        sample_data = helpers.make_sample_object(sample_df, params)
        # logging.info(sample_data)

        # feature data
        feature_df = helpers.get_feature_df(params)
        feature_data = helpers.make_feature_object(feature_df, params)
        # logging.info(feature_data)

        # qsip object
        q = helpers.make_qsip_object(source_data, sample_data, feature_data)
        logging.info(q)

        return {}
