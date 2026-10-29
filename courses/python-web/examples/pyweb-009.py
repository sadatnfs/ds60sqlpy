"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    import asyncio

    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient
    from flask import Flask, request

    wsgi = Flask(__name__)

    @wsgi.get("/interface")
    def sync_view():
        return {"interface": "WSGI", "version": list(request.environ["wsgi.version"])}

    asgi = FastAPI()

    @asgi.get("/interface")
    async def async_view(request: Request):
        await asyncio.sleep(0)
        return {"interface": "ASGI", "scope": request.scope["type"]}

    with wsgi.test_client() as client:
        wsgi_result = client.get("/interface").json
    with TestClient(asgi) as client:
        asgi_result = client.get("/interface").json()
    assert wsgi_result == {"interface": "WSGI", "version": [1, 0]}
    assert asgi_result == {"interface": "ASGI", "scope": "http"}
    return {
        "synchronous_application": wsgi_result,
        "asynchronous_application": asgi_result,
        "network_or_throughput_benchmark": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
