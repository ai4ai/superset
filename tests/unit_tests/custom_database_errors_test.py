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

import re

from superset.custom_database_errors import CUSTOM_DATABASE_ERRORS
from superset.errors import SupersetErrorType


def test_custom_database_errors_has_examples() -> None:
    assert "examples" in CUSTOM_DATABASE_ERRORS


def test_custom_database_errors_examples_patterns_are_regex() -> None:
    for pattern in CUSTOM_DATABASE_ERRORS["examples"]:
        assert isinstance(pattern, re.Pattern)


def test_custom_database_errors_examples_table_a() -> None:
    patterns = CUSTOM_DATABASE_ERRORS["examples"]
    matching_pattern = None
    for pattern, (message, error_type, extra) in patterns.items():
        if pattern.search("no such table: a"):
            matching_pattern = (message, error_type, extra)
            break
    assert matching_pattern is not None
    message, error_type, extra = matching_pattern
    assert error_type == SupersetErrorType.GENERIC_DB_ENGINE_ERROR
    assert "custom_doc_links" in extra
    assert extra["show_issue_info"] is False


def test_custom_database_errors_examples_table_b() -> None:
    patterns = CUSTOM_DATABASE_ERRORS["examples"]
    matching_pattern = None
    for pattern, (message, error_type, extra) in patterns.items():
        if pattern.search("no such table: b"):
            matching_pattern = (message, error_type, extra)
            break
    assert matching_pattern is not None
    message, error_type, extra = matching_pattern
    assert error_type == SupersetErrorType.GENERIC_DB_ENGINE_ERROR
    assert extra["show_issue_info"] is True


def test_custom_database_errors_no_match() -> None:
    patterns = CUSTOM_DATABASE_ERRORS["examples"]
    for pattern in patterns:
        assert not pattern.search("some completely unrelated error")


def test_custom_database_errors_tuple_structure() -> None:
    for db_name, patterns in CUSTOM_DATABASE_ERRORS.items():
        for pattern, value in patterns.items():
            assert isinstance(value, tuple), (
                f"Value for {db_name}/{pattern} is not a tuple"
            )
            assert len(value) == 3, (
                f"Tuple for {db_name}/{pattern} should have 3 elements"
            )
            message, error_type, extra = value
            assert isinstance(message, str), (
                f"Message should be str for {db_name}/{pattern}"
            )
            assert isinstance(error_type, SupersetErrorType)
            assert isinstance(extra, dict)
