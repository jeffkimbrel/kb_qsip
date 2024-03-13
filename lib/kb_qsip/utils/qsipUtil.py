import os
import datetime
import logging
import json
import uuid

from installed_clients.WorkspaceClient import Workspace as Workspace
from installed_clients.KBaseReportClient import KBaseReport

class qsipUtil:

    def __init__(self, config):
        self.config = config
        self.timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.callback_url = config['SDK_CALLBACK_URL']
        self.scratch = config['scratch']
        self.kbr = KBaseReport(self.callback_url)
        self.ws_client = Workspace(config["workspace-url"])

    def run(self, ctx, params):
        logging.info("*****Running run method of qsipUtil")
        return({})