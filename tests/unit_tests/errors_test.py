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


from superset.errors import (
    ERROR_TYPES_TO_ISSUE_CODES_MAPPING,
    ErrorLevel,
    ISSUE_CODES,
    SupersetError,
    SupersetErrorType,
)


def test_superset_error_type_values() -> None:
    assert SupersetErrorType.FRONTEND_CSRF_ERROR == "FRONTEND_CSRF_ERROR"
    assert SupersetErrorType.GENERIC_DB_ENGINE_ERROR == "GENERIC_DB_ENGINE_ERROR"
    assert SupersetErrorType.SYNTAX_ERROR == "SYNTAX_ERROR"
    assert SupersetErrorType.GENERIC_BACKEND_ERROR == "GENERIC_BACKEND_ERROR"


def test_error_level_values() -> None:
    assert ErrorLevel.INFO == "info"
    assert ErrorLevel.WARNING == "warning"
    assert ErrorLevel.ERROR == "error"


def test_superset_error_to_dict_basic() -> None:
    error = SupersetError(
        message="Something went wrong",
        error_type=SupersetErrorType.GENERIC_BACKEND_ERROR,
        level=ErrorLevel.ERROR,
    )
    result = error.to_dict()
    assert result["message"] == "Something went wrong"
    assert result["error_type"] == SupersetErrorType.GENERIC_BACKEND_ERROR


def test_superset_error_to_dict_with_extra() -> None:
    error = SupersetError(
        message="Bad query",
        error_type=SupersetErrorType.GENERIC_BACKEND_ERROR,
        level=ErrorLevel.ERROR,
        extra={"detail": "some detail"},
    )
    result = error.to_dict()
    assert "extra" in result
    assert "detail" in result["extra"]
    assert "issue_codes" in result["extra"]


def test_superset_error_post_init_populates_issue_codes() -> None:
    error = SupersetError(
        message="timeout",
        error_type=SupersetErrorType.BACKEND_TIMEOUT_ERROR,
        level=ErrorLevel.ERROR,
    )
    assert error.extra is not None
    assert "issue_codes" in error.extra
    codes = [ic["code"] for ic in error.extra["issue_codes"]]
    assert 1000 in codes
    assert 1001 in codes


def test_superset_error_post_init_no_issue_codes_for_unmapped_type() -> None:
    error = SupersetError(
        message="csrf",
        error_type=SupersetErrorType.FRONTEND_CSRF_ERROR,
        level=ErrorLevel.INFO,
    )
    assert error.extra is None


def test_superset_error_post_init_preserves_existing_extra() -> None:
    error = SupersetError(
        message="err",
        error_type=SupersetErrorType.GENERIC_DB_ENGINE_ERROR,
        level=ErrorLevel.ERROR,
        extra={"engine": "postgres"},
    )
    assert error.extra is not None
    assert error.extra["engine"] == "postgres"
    assert "issue_codes" in error.extra


def test_issue_codes_mapping_consistency() -> None:
    for error_type, codes in ERROR_TYPES_TO_ISSUE_CODES_MAPPING.items():
        for code in codes:
            assert code in ISSUE_CODES, (
                f"Issue code {code} mapped from {error_type} not in ISSUE_CODES"
            )


def test_superset_error_to_dict_without_extra() -> None:
    error = SupersetError(
        message="csrf error",
        error_type=SupersetErrorType.FRONTEND_CSRF_ERROR,
        level=ErrorLevel.INFO,
    )
    result = error.to_dict()
    assert "extra" not in result
    assert result["message"] == "csrf error"
    assert result["error_type"] == SupersetErrorType.FRONTEND_CSRF_ERROR
