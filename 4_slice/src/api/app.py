import json
import uuid
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server
from src.domain.assistant import AssistantUnavailable, safe_answer
from src.infra.assistant_adapter import FactOnlyAssistantAdapter
from src.infra.repositories import InMemoryPointRepository


def error(start_response, status, code, message):
    body = json.dumps({"code": code, "message": message, "traceId": str(uuid.uuid4())}).encode()
    start_response(status, [("Content-Type", "application/json"), ("Content-Length", str(len(body)))])
    return [body]


def create_app(repository=None, assistant=None):
    repository = repository or InMemoryPointRepository()
    assistant = assistant or FactOnlyAssistantAdapter()

    def app(environ, start_response):
        method, path = environ["REQUEST_METHOD"], environ["PATH_INFO"]
        if method == "GET" and path == "/points":
            query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
            try:
                limit, offset = int(query.get("limit", [20])[0]), int(query.get("offset", [0])[0])
                if not 1 <= limit <= 100 or offset < 0:
                    raise ValueError
            except ValueError:
                return error(
                    start_response, "400 Bad Request", "INVALID_PAGINATION", "limit must be 1..100 and offset >= 0"
                )
            items, total = repository.list(limit, offset)
            return respond(
                start_response,
                "200 OK",
                {"items": [x.to_dict() for x in items], "limit": limit, "offset": offset, "total": total},
            )
        if method == "GET" and path.startswith("/points/"):
            point = repository.get(path.rsplit("/", 1)[1])
            if point:
                return respond(start_response, "200 OK", point.to_dict())
            return error(start_response, "404 Not Found", "POINT_NOT_FOUND", "Point was not found")
        if method == "POST" and path == "/ask":
            try:
                payload = json.loads(environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0)) or b"{}")
                point_id, question = payload["pointId"], payload["question"]
                if (not isinstance(point_id, str) or not point_id.strip()
                        or not isinstance(question, str) or not question.strip() or len(question) > 300):
                    raise ValueError
            except (KeyError, TypeError, ValueError, UnicodeDecodeError):
                return error(
                    start_response,
                    "422 Unprocessable Entity",
                    "INVALID_ASK",
                    "pointId and a non-empty question are required",
                )
            point = repository.get(point_id)
            if not point:
                return error(start_response, "404 Not Found", "POINT_NOT_FOUND", "Point was not found")
            try:
                answer = safe_answer(point, question, assistant)
            except AssistantUnavailable:
                return error(
                    start_response,
                    "503 Service Unavailable",
                    "ASSISTANT_UNAVAILABLE",
                    "Assistant is temporarily unavailable",
                )
            return respond(start_response, "200 OK", {"answer": answer, "source": "FACTUAL_ASSISTANT"})
        return error(start_response, "404 Not Found", "ROUTE_NOT_FOUND", "Route was not found")
    return app


def respond(start_response, status, payload):
    body = json.dumps(payload).encode()
    start_response(status, [("Content-Type", "application/json"), ("Content-Length", str(len(body)))])
    return [body]


if __name__ == "__main__":
    print("Listening on http://localhost:8000")
    make_server("", 8000, create_app()).serve_forever()
