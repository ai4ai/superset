# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import logging
from unittest.mock import MagicMock

import pytest

from superset.stats_logger import BaseStatsLogger, DummyStatsLogger, StatsdStatsLogger

statsd_available = False
try:
    from statsd import StatsClient  # noqa: F401

    statsd_available = True
except ModuleNotFoundError:
    pass


def test_base_stats_logger_key_with_prefix() -> None:
    logger = DummyStatsLogger(prefix="myapp")
    assert logger.key(".requests") == "myapp.requests"


def test_base_stats_logger_key_without_prefix() -> None:
    logger = DummyStatsLogger(prefix="")
    assert logger.key("requests") == "requests"


def test_base_stats_logger_default_prefix() -> None:
    logger = DummyStatsLogger()
    assert logger.prefix == "superset"
    assert logger.key(".metric") == "superset.metric"


def test_base_stats_logger_abstract_methods() -> None:
    with pytest.raises(NotImplementedError):
        BaseStatsLogger().incr("key")
    with pytest.raises(NotImplementedError):
        BaseStatsLogger().decr("key")
    with pytest.raises(NotImplementedError):
        BaseStatsLogger().timing("key", 1.0)
    with pytest.raises(NotImplementedError):
        BaseStatsLogger().gauge("key", 1.0)


def test_dummy_stats_logger_incr(caplog: pytest.LogCaptureFixture) -> None:
    logger = DummyStatsLogger()
    with caplog.at_level(logging.DEBUG, logger="superset.stats_logger"):
        logger.incr("test.counter")
    assert any(
        "(incr)" in r.message and "test.counter" in r.message for r in caplog.records
    )


def test_dummy_stats_logger_decr(caplog: pytest.LogCaptureFixture) -> None:
    logger = DummyStatsLogger()
    with caplog.at_level(logging.DEBUG, logger="superset.stats_logger"):
        logger.decr("test.counter")
    assert any(
        "(decr)" in r.message and "test.counter" in r.message for r in caplog.records
    )


def test_dummy_stats_logger_timing(caplog: pytest.LogCaptureFixture) -> None:
    logger = DummyStatsLogger()
    with caplog.at_level(logging.DEBUG, logger="superset.stats_logger"):
        logger.timing("test.timing", 42.5)
    assert any(
        "(timing)" in r.message and "test.timing" in r.message for r in caplog.records
    )


def test_dummy_stats_logger_gauge(caplog: pytest.LogCaptureFixture) -> None:
    logger = DummyStatsLogger()
    with caplog.at_level(logging.DEBUG, logger="superset.stats_logger"):
        logger.gauge("test.gauge", 100.0)
    assert any(
        "(gauge)" in r.message and "test.gauge" in r.message for r in caplog.records
    )


@pytest.mark.skipif(not statsd_available, reason="statsd package not installed")
def test_statsd_stats_logger_with_client() -> None:
    mock_client = MagicMock()
    logger = StatsdStatsLogger(statsd_client=mock_client)
    assert logger.client is mock_client


@pytest.mark.skipif(not statsd_available, reason="statsd package not installed")
def test_statsd_stats_logger_incr_delegates() -> None:
    mock_client = MagicMock()
    logger = StatsdStatsLogger(statsd_client=mock_client)
    logger.incr("counter")
    mock_client.incr.assert_called_once_with("counter")


@pytest.mark.skipif(not statsd_available, reason="statsd package not installed")
def test_statsd_stats_logger_decr_delegates() -> None:
    mock_client = MagicMock()
    logger = StatsdStatsLogger(statsd_client=mock_client)
    logger.decr("counter")
    mock_client.decr.assert_called_once_with("counter")


@pytest.mark.skipif(not statsd_available, reason="statsd package not installed")
def test_statsd_stats_logger_timing_delegates() -> None:
    mock_client = MagicMock()
    logger = StatsdStatsLogger(statsd_client=mock_client)
    logger.timing("response_time", 250.0)
    mock_client.timing.assert_called_once_with("response_time", 250.0)


@pytest.mark.skipif(not statsd_available, reason="statsd package not installed")
def test_statsd_stats_logger_gauge_delegates() -> None:
    mock_client = MagicMock()
    logger = StatsdStatsLogger(statsd_client=mock_client)
    logger.gauge("active_connections", 5.0)
    mock_client.gauge.assert_called_once_with("active_connections", 5.0)


@pytest.mark.skipif(statsd_available, reason="statsd package is installed")
def test_statsd_stats_logger_raises_when_statsd_not_installed() -> None:
    with pytest.raises(ModuleNotFoundError):
        StatsdStatsLogger()
