# -*- coding: utf-8 -*-
# BEGIN_HEADER
import logging
import os

from kb_qsip.utils.qsip_util import QsipUtil

# END_HEADER


class kb_qsip:
    """
    Module Name:
    kb_qsip

    Module Description:
    A KBase module: kb_qsip
    """

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.1.3"
    GIT_URL = "https://github.com/jeffkimbrel/kb_qsip"
    GIT_COMMIT_HASH = "80edfe05396ea25de3fa730134a873de1aafbb08"

    # BEGIN_CLASS_HEADER
    # END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        # BEGIN_CONSTRUCTOR
        config["callback_url"] = os.environ["SDK_CALLBACK_URL"]
        self.config = config

        logging.basicConfig(
            format="%(created)s %(levelname)s: %(message)s", level=logging.INFO
        )
        # END_CONSTRUCTOR
        pass

    def run_kb_qsip(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        # BEGIN run_kb_qsip
        qsip_runner = QsipUtil(self.config, ctx)
        output = qsip_runner.run(params)
        # END run_kb_qsip

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError(
                "Method run_kb_qsip "
                + "return value output "
                + "is not type dict as required."
            )
        # return the results
        return [output]

    def status(self, ctx):
        # BEGIN_STATUS
        returnVal = {
            "state": "OK",
            "message": "",
            "version": self.VERSION,
            "git_url": self.GIT_URL,
            "git_commit_hash": self.GIT_COMMIT_HASH,
        }
        # END_STATUS
        return [returnVal]
