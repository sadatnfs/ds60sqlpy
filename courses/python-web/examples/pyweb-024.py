"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    import httpx2
    from flask import Flask

    def transport(request):
        if request.url.path == "/valid":
            return httpx2.Response(200, json={"value": 7})
        if request.url.path == "/slow":
            raise httpx2.ReadTimeout("fixture timeout", request=request)
        return httpx2.Response(503, json={"error": "fixture unavailable"})

    upstream = httpx2.Client(
        transport=httpx2.MockTransport(transport), base_url="https://upstream.example", timeout=1
    )
    app = Flask(__name__)

    @app.get("/proxy/<case>")
    def proxy(case):
        if case not in {"valid", "slow", "down"}:
            return {"error": "unsupported case"}, 404
        try:
            response = upstream.get("/" + case)
            response.raise_for_status()
        except httpx2.TimeoutException:
            return {"error": "upstream timeout"}, 504
        except httpx2.HTTPStatusError:
            return {"error": "upstream unavailable"}, 502
        return {"value": response.json()["value"]}

    try:
        client = app.test_client()
        assert client.get("/proxy/valid").json == {"value": 7}
        assert client.get("/proxy/slow").status_code == 504
        assert client.get("/proxy/down").status_code == 502
        return {
            "success": 200,
            "upstream_timeout": 504,
            "upstream_failure": 502,
            "transport": "actual HTTPX2 MockTransport; no remote requests",
        }
    finally:
        upstream.close()


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
