import datetime
import logging
import uuid

from rpy2 import robjects
from rpy2.robjects.packages import importr, data


import kb_qsip.utils.helpers as helpers

from installed_clients.WorkspaceClient import Workspace
from installed_clients.KBaseReportClient import KBaseReport


class qsipUtil:

    def __init__(self, config):
        self.config = config
        self.timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.callback_url = config["SDK_CALLBACK_URL"]
        self.scratch = config["scratch"]
        self.kbr = KBaseReport(self.callback_url)
        self.ws_client = Workspace(config["workspace-url"])

    def run(self, ctx, params):

        qsip2 = importr("qSIP2")
        qsip2_data = data(qsip2)
        logging.info(qsip2.__version__)

        # source data
        source_df = helpers.get_source_df(
            params, Workspace(self.config["workspace-url"], token=ctx.get("token"))
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
