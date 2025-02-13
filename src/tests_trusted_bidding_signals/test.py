# Copyright 2021 RTBHOUSE. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import logging

from assertpy import assert_that
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from common.utils import print_debug
from common.utils import log_exception
from common.utils import measure_time
from common.utils import pretty_json
from common.utils import MeasureDuration
from common.mockserver import MockServer
from common.base_test import BaseTest

logger = logging.getLogger(__file__)


class TrustedBiddingSignalsTest(BaseTest):

    @print_debug
    @measure_time
    @log_exception
    def test__should_pass_trusted_bidding_signals(self):
        with MockServer(8101, '/home/usertd/tests/tests_trusted_bidding_signals/resources/buyer') as buyer_server,\
                MockServer(8102, '/home/usertd/tests/tests_trusted_bidding_signals/resources/seller') as seller_server:

            with MeasureDuration("joinAdInterestGroup"):
                self.driver.get(buyer_server.address)
                self.assertDriverContainsText('body', 'joined interest group')

            with MeasureDuration("runAdAuction"):
                self.driver.get(seller_server.address)
                WebDriverWait(self.driver, 5)\
                    .until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe')))
                self.assertDriverContainsText('body', 'TC AD 1')

        report_win_signals = buyer_server.get_first_request("/reportWin").get_first_json_param('signals')
        logger.info(f"reportWin() signals: {pretty_json(report_win_signals)}")
        # generateBid() in this test case uses one of trustedBiddingSignals as a bid value
        assert_that(report_win_signals.get('browserSignals').get('bid')).is_equal_to(15)