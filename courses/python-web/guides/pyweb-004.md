# pyweb-004: Headers, JSON, bytes and content negotiation

Tutorial mode. Stage: beginner. Direct prerequisites: `pyweb-003`.

## Starting point and result

HTTP carries bytes. Applications interpret those bytes using a media type and an encoding. JSON is one representation format, not a synonym for every request body. This chapter distinguishes a valid JSON object, malformed JSON and a body sent with an unsupported media type.

## Mechanism: parse only the declared representation

The echo endpoint first checks `request.is_json`. If the request is not declared as JSON, it returns 415 Unsupported Media Type. It then attempts JSON parsing and requires an object with a string `text` field. A body that cannot satisfy that contract returns 400 in this particular example.

The `Content-Type` request header describes the body the client sent. The `Accept` header describes representations the client can accept in the response. They answer different questions. The demonstration sends an Accept preference but the endpoint has only one documented response format. It does not implement a complete quality-weighted content-negotiation algorithm.

Text length also depends on the unit being counted. Python's `len("café")` returns four Unicode code points for this spelling. Encoding it as UTF-8 produces five bytes. Neither number is a universal count of visible glyphs: combining characters and grapheme clusters add another layer. Choose the relevant unit for storage, transport and user-facing limits.

## Worked case: a valid Unicode representation

The client sends a JSON object containing `café`. Flask parses it as a Python string, the handler counts its characters and the response is decoded back into a JSON object. The program checks the semantic value and the separate UTF-8 byte length.

JSON serializers may escape some characters or emit them directly as UTF-8. Two byte sequences can therefore decode to the same application value. Use semantic comparisons when testing the data contract. When computing a strong ETag or a signature over a representation, define and test the exact bytes instead; that later topic has a stricter requirement.

## Worked case: malformed versus unsupported input

The malformed request advertises JSON but ends halfway through an object. Parsing cannot produce the required value, so the endpoint returns 400. The plain-text request contains valid text but uses `text/plain`; this endpoint does not accept that representation, so it returns 415.

Keeping these cases distinct gives clients useful feedback. Treating every body as JSON regardless of its header can hide mistakes. Treating every parse failure as an internal server error incorrectly blames the server for input that violated the contract.

The handler uses silent parsing so it can provide its own controlled error representation. That does not mean errors should be ignored. The parsed result is explicitly checked, and invalid input never reaches the success branch.

## Failure diagnosis

A client that receives HTML while expecting JSON may be looking at a framework error page, a proxy response or a route that returns a different representation. Inspect status and Content-Type before calling a JSON decoder. Character corruption often reflects an encoding mismatch or repeated encode/decode operations. Avoid solving those problems by arbitrarily discarding undecodable bytes.

For real services, place explicit bounds on body size and parsing cost. This example's tiny inputs establish representation behavior; they do not establish resistance to huge documents or compressed payload expansion.

## Interview discussion

**What is the difference between Content-Type and Accept?** Content-Type identifies the body being sent. Accept expresses response preferences. A server must define which representations it actually supports.

**Why can character and byte limits differ?** An encoding maps characters to bytes, often using more than one byte for a character. A transport budget and a user-visible text limit may require different checks.

## Next step

Describe accepted fields and types explicitly. A parsed JSON object still needs validation before it becomes an application command.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, request

    app = Flask(__name__)

    @app.post("/echo")
    def echo():
        if not request.is_json:
            return {"error": "application/json is required"}, 415
        value = request.get_json(silent=True)
        if not isinstance(value, dict) or not isinstance(value.get("text"), str):
            return {"error": "a JSON object with text is required"}, 400
        return {"text": value["text"], "characters": len(value["text"])}

    with app.test_client() as client:
        valid = client.post("/echo", json={"text": "café"}, headers={"Accept": "application/json"})
        malformed = client.post("/echo", data=b'{"text":', content_type="application/json")
        wrong_type = client.post("/echo", data="café", content_type="text/plain; charset=utf-8")
        assert valid.json == {"text": "café", "characters": 4}
        assert malformed.status_code == 400 and wrong_type.status_code == 415
        assert len("café".encode()) == 5
    return {
        "parsed_representation": valid.json,
        "utf8_bytes": 5,
        "malformed_status": 400,
        "unsupported_media_type_status": 415,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
