"""Main kb_qsip code."""

import logging
import uuid
import os

from typing import Any

from installed_clients.KBaseReportClient import KBaseReport

from pandas import DataFrame

from rpy2 import robjects
from rpy2.robjects import pandas2ri
from rpy2.robjects.methods import RS4

from kb_qsip.utils import helpers


class QsipUtil:
    """Core qsip execution code."""

    def __init__(
        self: "QsipUtil", config: dict[str, Any], context: dict[str, Any]
    ) -> None:
        """Initialise the qsip app."""
        self.config = config
        self.scratch = config['scratch']
        self.context = context

        self.token: str = context.get("token", "")
        if not self.token:
            err_msg = "Auth token required to access workspace data"
            raise RuntimeError(err_msg)

        # self.callback_url = config.get("callback_url")
        # if not self.callback_url:
        #     err_msg = "SDK_CALLBACK_URL env var required to make KBase report"
        #     raise RuntimeError(err_msg)
        # self.kbr = KBaseReport(self.callback_url)

    def run(self: "QsipUtil", params: dict[str, Any]):
        """Run the qsip app.

        :param self: class instance
        :type self: QsipUtil
        :param params: parameters from the app UI
        :type params: dict[str, Any]
        :return: output of running the qSIP2 R package
        :rtype: ???
        """
        if "debug" in params and params["debug"]:
            dataframes_by_ref: dict[str, RS4] = (
                helpers.retrieve_object_dataframes_from_qsip2_data(params)
            )
            # convert these
        else:
            # retrieve the data from the workspace, indexed by their KBase UPA
            converted_data = helpers.retrieve_convert_objects(
                params, self.config, self.token
            )
            dataframes_by_ref: dict[str, RS4] = {}
            # these can all be converted into dataframes
            with (robjects.default_converter + pandas2ri.converter).context():
                for ref in converted_data:
                    dataframes_by_ref[
                        ref
                    ] = robjects.conversion.get_conversion().py2rpy(
                        DataFrame(converted_data[ref]["dict_list"])
                    )


        # make scratch_directory
        output_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        os.mkdir(output_directory)

        # qsip object
        qsip_object = helpers.make_qsip_object(dataframes_by_ref, params)

        # do whatever to q
        qsip_object = helpers.run_feature_filter(qsip_object, params)
        qsip_object = helpers.run_resampling(qsip_object, params)
        qsip_object = helpers.run_EAF_calculations(qsip_object, params)

        eaf_summary = helpers.summarize_EAF_values(qsip_object, params)
        helpers.write_EAF_summary(eaf_summary, output_directory)

        # plots
        helpers.plot_source_wads(qsip_object, output_directory, params)
        helpers.plot_filter_results(qsip_object, output_directory)
        

        report_params = {
            'message': '',
            'html_links': [],
            'direct_html_link_index': 0,
            'objects_created': [],
            'workspace_name': params['workspace_name'],
            'report_object_name': f'qsip_{uuid.uuid4()}'}

        report_output = self.kbr.create_extended_report(report_params)

        return {'report_name': report_output['name'],
                'report_ref': report_output['ref']}
                
