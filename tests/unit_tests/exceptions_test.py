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

from collections import defaultdict

from marshmallow import ValidationError

from superset.errors import ErrorLevel, SupersetError, SupersetErrorType
from superset.exceptions import (
    AdvancedDataTypeResponseError,
    CacheLoadError,
    CertificateException,
    ColumnNotFoundException,
    DashboardImportException,
    DatabaseNotFoundException,
    DatasetInvalidPermissionEvaluationException,
    InvalidPayloadFormatError,
    InvalidPayloadSchemaError,
    InvalidPostProcessingError,
    MissingUserContextException,
    NoDataException,
    NullValueException,
    OAuth2Error,
    OAuth2RedirectError,
    QueryClauseValidationException,
    QueryNotFoundException,
    QueryObjectValidationError,
    SerializationError,
    SpatialException,
    SupersetCancelQueryException,
    SupersetDisallowedSQLFunctionException,
    SupersetDisallowedSQLTableException,
    SupersetErrorException,
    SupersetErrorFromParamsException,
    SupersetErrorsException,
    SupersetException,
    SupersetGenericDBErrorException,
    SupersetGenericErrorException,
    SupersetMarshmallowValidationError,
    SupersetParseError,
    SupersetSecurityException,
    SupersetSyntaxErrorException,
    SupersetTemplateException,
    SupersetTemplateParamsErrorException,
    SupersetTimeoutException,
    SupersetVizException,
    TableNotFoundException,
)


def test_superset_exception_defaults() -> None:
    exc = SupersetException()
    assert exc.status == 500
    assert exc.message == ""
    assert exc.exception is None
    assert exc.error_type is None


def test_superset_exception_with_message() -> None:
    exc = SupersetException("something broke")
    assert exc.message == "something broke"
    assert str(exc) == "something broke"


def test_superset_exception_with_nested_exception() -> None:
    inner = ValueError("inner error")
    exc = SupersetException("outer", exception=inner)
    assert exc.exception is inner


def test_superset_exception_with_error_type() -> None:
    exc = SupersetException("err", error_type=SupersetErrorType.GENERIC_BACKEND_ERROR)
    assert exc.error_type == SupersetErrorType.GENERIC_BACKEND_ERROR


def test_superset_exception_to_dict() -> None:
    exc = SupersetException("msg", error_type=SupersetErrorType.GENERIC_BACKEND_ERROR)
    d = exc.to_dict()
    assert d["message"] == "msg"
    assert d["error_type"] == SupersetErrorType.GENERIC_BACKEND_ERROR


def test_superset_exception_to_dict_with_nested_to_dict() -> None:
    class InnerError(Exception):
        def to_dict(self) -> dict[str, str]:
            return {"inner_key": "inner_val"}

    inner = InnerError()
    exc = SupersetException("outer", exception=inner)
    d = exc.to_dict()
    assert d["message"] == "outer"
    assert d["inner_key"] == "inner_val"


def test_superset_error_exception() -> None:
    error = SupersetError(
        message="err",
        error_type=SupersetErrorType.GENERIC_BACKEND_ERROR,
        level=ErrorLevel.ERROR,
    )
    exc = SupersetErrorException(error)
    assert exc.status == 500
    assert exc.error is error
    assert exc.to_dict() == error.to_dict()


def test_superset_error_exception_custom_status() -> None:
    error = SupersetError(
        message="err",
        error_type=SupersetErrorType.GENERIC_BACKEND_ERROR,
        level=ErrorLevel.ERROR,
    )
    exc = SupersetErrorException(error, status=503)
    assert exc.status == 503


def test_superset_generic_error_exception() -> None:
    exc = SupersetGenericErrorException("generic failure")
    assert exc.error.error_type == SupersetErrorType.GENERIC_BACKEND_ERROR
    assert exc.error.level == ErrorLevel.ERROR
    assert exc.error.message == "generic failure"


def test_superset_generic_error_exception_custom_status() -> None:
    exc = SupersetGenericErrorException("fail", status=502)
    assert exc.status == 502


def test_superset_error_from_params_exception() -> None:
    exc = SupersetErrorFromParamsException(
        error_type=SupersetErrorType.SYNTAX_ERROR,
        message="bad sql",
        level=ErrorLevel.ERROR,
        extra={"sql": "SELECT *"},
    )
    assert exc.error.error_type == SupersetErrorType.SYNTAX_ERROR
    assert exc.error.message == "bad sql"
    assert exc.error.extra is not None
    assert exc.error.extra["sql"] == "SELECT *"


def test_superset_errors_exception() -> None:
    errors = [
        SupersetError(
            message="err1",
            error_type=SupersetErrorType.GENERIC_BACKEND_ERROR,
            level=ErrorLevel.ERROR,
        ),
        SupersetError(
            message="err2",
            error_type=SupersetErrorType.SYNTAX_ERROR,
            level=ErrorLevel.WARNING,
        ),
    ]
    exc = SupersetErrorsException(errors)
    assert exc.errors == errors
    assert exc.status == 500


def test_superset_errors_exception_custom_status() -> None:
    exc = SupersetErrorsException([], status=422)
    assert exc.status == 422


def test_superset_syntax_error_exception() -> None:
    errors = [
        SupersetError(
            message="syntax err",
            error_type=SupersetErrorType.SYNTAX_ERROR,
            level=ErrorLevel.ERROR,
        ),
    ]
    exc = SupersetSyntaxErrorException(errors)
    assert exc.status == 422
    assert exc.error_type == SupersetErrorType.SYNTAX_ERROR


def test_superset_timeout_exception() -> None:
    exc = SupersetTimeoutException(
        error_type=SupersetErrorType.BACKEND_TIMEOUT_ERROR,
        message="timed out",
        level=ErrorLevel.ERROR,
    )
    assert exc.status == 408


def test_superset_generic_db_error_exception() -> None:
    exc = SupersetGenericDBErrorException("db error")
    assert exc.status == 400
    assert exc.error.error_type == SupersetErrorType.GENERIC_DB_ENGINE_ERROR
    assert exc.error.level == ErrorLevel.ERROR


def test_superset_generic_db_error_exception_with_extra() -> None:
    exc = SupersetGenericDBErrorException("db error", extra={"engine": "mysql"})
    assert exc.error.extra is not None
    assert exc.error.extra["engine"] == "mysql"


def test_superset_template_params_error_exception() -> None:
    exc = SupersetTemplateParamsErrorException(
        message="missing param",
        error=SupersetErrorType.MISSING_TEMPLATE_PARAMS_ERROR,
    )
    assert exc.status == 400
    assert exc.error.error_type == SupersetErrorType.MISSING_TEMPLATE_PARAMS_ERROR


def test_superset_security_exception() -> None:
    error = SupersetError(
        message="access denied",
        error_type=SupersetErrorType.TABLE_SECURITY_ACCESS_ERROR,
        level=ErrorLevel.ERROR,
    )
    exc = SupersetSecurityException(error, payload={"table": "secret_table"})
    assert exc.status == 403
    assert exc.payload == {"table": "secret_table"}


def test_simple_exception_status_codes() -> None:
    assert SupersetVizException([]).status == 400
    assert NoDataException().status == 400
    assert NullValueException().status == 400
    assert SupersetTemplateException().status == 422
    assert DatabaseNotFoundException("msg").status == 404
    assert MissingUserContextException().status == 422
    assert QueryObjectValidationError().status == 400
    assert AdvancedDataTypeResponseError().status == 400
    assert InvalidPostProcessingError().status == 400
    assert CacheLoadError().status == 404
    assert QueryClauseValidationException().status == 400
    assert SupersetCancelQueryException().status == 422
    assert QueryNotFoundException().status == 404
    assert ColumnNotFoundException().status == 404


def test_spatial_exception_inherits_superset_exception() -> None:
    exc = SpatialException("spatial error")
    assert isinstance(exc, SupersetException)


def test_certificate_exception_default_message() -> None:
    exc = CertificateException()
    assert exc.message is not None


def test_dashboard_import_exception() -> None:
    exc = DashboardImportException("import failed")
    assert isinstance(exc, SupersetException)


def test_dataset_invalid_permission_evaluation_exception() -> None:
    exc = DatasetInvalidPermissionEvaluationException("can't compute")
    assert isinstance(exc, SupersetException)


def test_serialization_error() -> None:
    exc = SerializationError("bad serialization")
    assert isinstance(exc, SupersetException)


def test_invalid_payload_format_error() -> None:
    exc = InvalidPayloadFormatError()
    assert exc.status == 400
    assert exc.error.error_type == SupersetErrorType.INVALID_PAYLOAD_FORMAT_ERROR


def test_invalid_payload_format_error_custom_message() -> None:
    exc = InvalidPayloadFormatError("custom message")
    assert exc.error.message == "custom message"


def test_invalid_payload_schema_error() -> None:
    validation_err = ValidationError({"field": ["Missing data."]})
    exc = InvalidPayloadSchemaError(validation_err)
    assert exc.status == 422
    assert exc.error.error_type == SupersetErrorType.INVALID_PAYLOAD_SCHEMA_ERROR
    assert exc.error.extra is not None
    assert "messages" in exc.error.extra


def test_invalid_payload_schema_error_with_defaultdict() -> None:
    messages: dict[str, defaultdict[str, list[str]]] = {
        "field": defaultdict(list, {"nested": ["err"]})
    }
    validation_err = ValidationError(messages)
    exc = InvalidPayloadSchemaError(validation_err)
    assert exc.error.extra is not None
    assert isinstance(exc.error.extra["messages"]["field"], dict)


def test_superset_marshmallow_validation_error() -> None:
    validation_err = ValidationError({"name": ["too long"]})
    exc = SupersetMarshmallowValidationError(
        validation_err, payload={"name": "x" * 500}
    )
    assert exc.status == 422
    assert exc.error.error_type == SupersetErrorType.MARSHMALLOW_ERROR
    assert exc.error.extra is not None
    assert exc.error.extra["payload"] == {"name": "x" * 500}
    assert exc.error.extra["messages"] == {"name": ["too long"]}


def test_superset_parse_error_default_message() -> None:
    exc = SupersetParseError(sql="SELECT * FORM table")
    assert exc.status == 422
    assert exc.error.error_type == SupersetErrorType.INVALID_SQL_ERROR
    assert exc.error.extra is not None
    assert exc.error.extra["sql"] == "SELECT * FORM table"


def test_superset_parse_error_with_highlight_and_position() -> None:
    exc = SupersetParseError(
        sql="SELECT * FORM t",
        engine="presto",
        highlight="FORM",
        line=1,
        column=10,
    )
    assert "FORM" in str(exc)
    assert exc.error.extra is not None
    assert exc.error.extra["engine"] == "presto"
    assert exc.error.extra["line"] == 1
    assert exc.error.extra["column"] == 10


def test_superset_parse_error_custom_message() -> None:
    exc = SupersetParseError(
        sql="bad sql",
        message="Custom parse error",
    )
    assert str(exc) == "Custom parse error"


def test_superset_parse_error_with_line_only() -> None:
    exc = SupersetParseError(
        sql="SELECT * FORM t",
        line=1,
    )
    assert exc.error.extra is not None
    assert exc.error.extra["line"] == 1


def test_oauth2_redirect_error() -> None:
    exc = OAuth2RedirectError(
        url="https://auth.example.com",
        tab_id="tab-123",
        redirect_uri="https://superset.example.com/callback",
    )
    assert exc.status == 403
    assert exc.error.error_type == SupersetErrorType.OAUTH2_REDIRECT
    assert exc.error.extra is not None
    assert exc.error.extra["url"] == "https://auth.example.com"
    assert exc.error.extra["tab_id"] == "tab-123"


def test_oauth2_error() -> None:
    exc = OAuth2Error("token expired")
    assert exc.error.error_type == SupersetErrorType.OAUTH2_REDIRECT_ERROR
    assert exc.error.extra is not None
    assert exc.error.extra["error"] == "token expired"


def test_superset_disallowed_sql_function_exception() -> None:
    exc = SupersetDisallowedSQLFunctionException({"SLEEP", "BENCHMARK"})
    assert exc.error.error_type == SupersetErrorType.SYNTAX_ERROR


def test_superset_disallowed_sql_table_exception() -> None:
    exc = SupersetDisallowedSQLTableException({"mysql.user"})
    assert exc.error.error_type == SupersetErrorType.SYNTAX_ERROR


def test_database_not_found_exception() -> None:
    exc = DatabaseNotFoundException("Database 'mydb' not found")
    assert exc.status == 404
    assert exc.error.error_type == SupersetErrorType.DATABASE_NOT_FOUND_ERROR


def test_table_not_found_exception() -> None:
    exc = TableNotFoundException("Table 'users' not found")
    assert exc.status == 404
    assert exc.error.error_type == SupersetErrorType.TABLE_NOT_FOUND_ERROR
