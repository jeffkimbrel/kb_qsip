# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from kb_qsip.kb_qsipImpl import kb_qsip
from kb_qsip.kb_qsipServer import MethodContext
from kb_qsip.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class kb_qsipTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_qsip'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_qsip',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = kb_qsip(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_kb_qsip_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_your_method(self):

        ret = self.serviceImpl.run_kb_qsip(self.ctx, {'workspace_name': self.wsName,
                                                      'debug': True,

                                                      # data files
                                                      'source_data': "72832/2/1",
                                                      'sample_data': "72832/3/1",
                                                      'feature_data': "72832/7/1",

                                                      # "M" denotes source_data
                                                      'M_isotope': 'Isotope', 
                                                      'M_source_mat_id' : 'source',
                                                      'M_isotopolog' : 'isotopolog',

                                                      # "S" denotes sample_data
                                                      'S_sample_id' : "sample", 
                                                      'S_source_mat_id' : "source",
                                                      'S_gradient_position' : "Fraction",
                                                      'S_gradient_pos_density' : "density_g_ml",
                                                      'S_gradient_pos_amt' : "avg_16S_g_soil",
                                                      'calculate_gradient_pos_rel_amt': True,
                                                      'S_gradient_pos_rel_amt' : "avg_16S_g_soil",

                                                      # "F" denotes feature_data
                                                      'F_feature_ids': "ASV", 
                                                      'F_type' : "counts",

                                                      # Analysis
                                                      "resamples": 1000,
                                                      "resample_success": 0.8,
                                                      "confidence": 0.9})
        