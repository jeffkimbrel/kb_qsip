# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os

from .utils.qsipUtil import qsipUtil
from kb_qsip.utils.qsipUtil import qsipUtil

from installed_clients.KBaseReportClient import KBaseReport
#END_HEADER


class kb_qsip:
    '''
    Module Name:
    kb_qsip

    Module Description:
    A KBase module: kb_qsip
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.config = config
        self.config['SDK_CALLBACK_URL'] = self.callback_url
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
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
        #BEGIN run_kb_qsip
        qsip_runner = qsipUtil(self.config)
        output = qsip_runner.run(ctx, params)
        #END run_kb_qsip


        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_qsip return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
