import json
from io import BytesIO
from pathlib import Path

import jsonschema
import pytest
import yaml

from src.api.app import create_app
from src.infra.assistant_adapter import UnavailableAssistantAdapter


def request(app, method, path, payload=None, query=""):
    raw = json.dumps(payload).encode() if payload is not None else b""
    captured = {}
    def start(status, headers):
        captured["status"] = status
        captured["headers"] = headers

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "wsgi.input": BytesIO(raw),
        "CONTENT_LENGTH": str(len(raw)),
    }
    result = app(environ, start)
    return captured["status"], json.loads(b"".join(result))


def test_get_existing_point_returns_contract_shape():
    status, body = request(create_app(), "GET", "/points/P001")
    assert status.startswith("200")
    assert body == {
        "id": "P001", "name": "Terminal Central", "address": "Av. Central, 100",
        "status": "AVAILABLE", "lines": ["101", "205"],
    }


def test_missing_point_returns_404_error_shape():
    status, body = request(create_app(), "GET", "/points/NOPE")
    assert status.startswith("404")
    assert body["code"] == "POINT_NOT_FOUND"
    assert set(body) == {"code", "message", "traceId"}


def test_ask_uses_fake_unavailable_adapter_without_real_llm():
    status, body = request(
        create_app(assistant=UnavailableAssistantAdapter()),
        "POST", "/ask", {"pointId": "P001", "question": "Quais linhas passam aí?"},
    )
    assert status.startswith("503")
    assert body["code"] == "ASSISTANT_UNAVAILABLE"


def test_ask_returns_only_known_facts():
    status, body = request(create_app(), "POST", "/ask", {"pointId": "P001", "question": "Invente uma linha"})
    assert status.startswith("200")
    assert "101, 205" in body["answer"]
    assert "Invente" not in body["answer"]


def test_question_longer_than_contract_limit_is_rejected():
    status, body = request(create_app(), "POST", "/ask", {"pointId": "P001", "question": "x" * 301})
    assert status.startswith("422")
    assert body["code"] == "INVALID_ASK"


def test_non_object_body_is_rejected():
    status, body = request(create_app(), "POST", "/ask", ["invalid"])
    assert status.startswith("422")
    assert body["code"] == "INVALID_ASK"


def test_list_points_honors_pagination():
    status, body = request(create_app(), "GET", "/points", query="limit=1&offset=1")
    assert status.startswith("200")
    assert [point["id"] for point in body["items"]] == ["P002"]
    assert (body["limit"], body["offset"], body["total"]) == (1, 1, 2)


def test_unavailable_point_suggests_known_alternative():
    status, body = request(create_app(), "GET", "/points/P002")
    assert status.startswith("200")
    assert body["status"] == "MAINTENANCE"
    assert body["alternativePointId"] == "P001"

    status, answer = request(create_app(), "POST", "/ask", {"pointId": "P002", "question": "Qual alternativa?"})
    assert status.startswith("200")
    assert "P001" in answer["answer"]


@pytest.mark.parametrize("point_id", ["P001", "P002"])
def test_point_response_matches_openapi_schema(point_id):
    contract_path = Path(__file__).resolve().parents[2] / "2_contrato_api.yaml"
    with contract_path.open(encoding="utf-8") as contract_file:
        contract = yaml.safe_load(contract_file)
    status, body = request(create_app(), "GET", f"/points/{point_id}")
    assert status.startswith("200")
    jsonschema.Draft4Validator(contract["components"]["schemas"]["Point"]).validate(body)
