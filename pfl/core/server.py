# Copyright (c) 2019 GalaxyLearning Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import threading
import logging
from pfl.core import communicate_server
from concurrent.futures import ThreadPoolExecutor
from pfl.core.aggregator import FedAvgAggregator
from pfl.utils.utils import LoggerFactory, CyclicTimer
from pfl.core.strategy import WorkModeStrategy, FederateStrategy
from pfl.exceptions.fl_expection import PFLException
from pfl.utils.ethereum_utils import PFLEthereumUtils

JOB_PATH = os.path.join(os.path.abspath("."), "res", "jobs_server")
BASE_MODEL_PATH = os.path.join(os.path.abspath("."), "res", "models")


class FLServer(object):

    def __init__(self):
        super(FLServer, self).__init__()
        self.logger = LoggerFactory.getLogger("FlServer", logging.INFO)

    def start(self):
        pass


class FLStandaloneServer(FLServer):
    """
    FLStandaloneServer is just responsible for running aggregator
    """

    def __init__(self, federate_strategy=FederateStrategy.FED_AVG):
        super(FLStandaloneServer, self).__init__()
        self.work_mode = WorkModeStrategy.WORKMODE_STANDALONE
        self.executor_pool = ThreadPoolExecutor(5)
        self.federate_strategy = federate_strategy
        if federate_strategy == FederateStrategy.FED_AVG:
            self.aggregator = FedAvgAggregator(WorkModeStrategy.WORKMODE_STANDALONE, JOB_PATH, BASE_MODEL_PATH)
        else:
            pass

    def start(self):
        self.logger.info("Work Mode: {}".format(self.work_mode))
        t = CyclicTimer(5, self.aggregator.aggregate)
        t.start()
        self.logger.info("{} Aggregator started".format(self.federate_strategy))


class FLClusterServer(FLServer):
    """
    FLClusterServer is responsible for running aggregator and communication server
    """

    def __init__(self, ip, port, api_version, federate_strategy=FederateStrategy.FED_AVG):
        super(FLClusterServer, self).__init__()
        self.executor_pool = ThreadPoolExecutor(5)
        if federate_strategy == FederateStrategy.FED_AVG:
            self.aggregator = FedAvgAggregator(WorkModeStrategy.WORKMODE_CLUSTER, JOB_PATH, BASE_MODEL_PATH)
        else:
            pass
        self.ip = ip
        self.port = port
        self.api_version = api_version
        self.federate_strategy = federate_strategy
        self.work_mode = WorkModeStrategy.WORKMODE_CLUSTER

    def start(self):
        self.logger.info("Work Mode: {}".format(self.work_mode))
        self.executor_pool.submit(communicate_server.start_communicate_server, self.api_version, self.ip, self.port)
        if self.federate_strategy == FederateStrategy.FED_AVG:
            t = CyclicTimer(5, self.aggregator.aggregate)
            t.start()
            self.logger.info("{} communication server started.".format(self.federate_strategy))
            self.logger.info("{} Aggregator started".format(self.federate_strategy))
        else:
            self.logger.info("{} communication server started.".format(self.federate_strategy))
            self.logger.info("{} aggregation mode has no server aggregator".format(self.federate_strategy))


# class FLServerBlockchain(FLServer):
#
#     def __init__(self, ethereum_url=None, server_blockchain_address=None, server_blockchain_address_password=None,
#                  federate_strategy=FederateStrategy.FED_DISTILLATION):
#         super(FLServerBlockchain, self).__init__()
#         if ethereum_url is None or server_blockchain_address is None or server_blockchain_address_password is None:
#             raise PFLException("parameter error")
#         self.federate_strategy = federate_strategy
#         self.server_blockchain_address = server_blockchain_address
#         self.server_blockchain_address_password = server_blockchain_address_password
#         self.work_mode = WorkModeStrategy.WORKMODE_BLOCKCHAIN
#         self.ethereum_url = ethereum_url
#         self.web3 = PFLEthereumUtils.get_connection_with_ethereum(self.ethereum_url)
#         self.pfl_controller_contract = PFLEthereumUtils.init_pfl_controller_contracts(web3=self.web3,
#                                                                                       account=self.server_blockchain_address,
#                                                                                       account_password=self.server_blockchain_address_password)
#         self.cyclic_timer = CyclicTimer(60, PFLEthereumUtils.block_support_function)
#
#     def start(self):
#         self.logger.info("Work Mode: {}".format(self.work_mode))
#         self.logger.info("Successfully connected to Ethereum")
#         if self.federate_strategy == FederateStrategy.FED_AVG:
#             raise PFLException("Blockchain mode only allowed in FED_DISTILLATION federate strategy")
#         self.cyclic_timer.start()