# pyweb-018: Flask forms and CSRF protection

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-017`.

## Starting point and result

A browser form needs both field validation and a decision about whether the request is authorized to use the client's ambient credentials. CSRF protection addresses one part of that request-origin problem. This chapter uses Flask-WTF and its actual CSRF machinery rather than substituting a manually checked placeholder field.

## Key terms

- **CSRF:** Cross-site request forgery: another site causes a browser to send a state-changing request that carries the user's ambient credentials.
- **Ambient credentials:** Credentials such as cookies that a browser attaches automatically to matching requests regardless of which page initiated them.
- **CSRF token:** A session-bound secret rendered into the form and required on submission, which a forging site cannot read; Flask-WTF rejects a missing token with 400.
- **hidden_tag():** A Flask-WTF form method that renders the form's hidden fields, including the CSRF token.
- **Field validator:** A rule such as DataRequired or Length that checks a submitted value, independently of CSRF validation.

## Mechanism: a form token participates in a larger session contract

The application enables CSRF protection and uses a test-only signing key. The form contains a name field with DataRequired and length validation. Rendering `hidden_tag()` supplies the framework's hidden fields, including the CSRF token. A client must return the appropriate token while retaining the associated session context.

Field validation and CSRF validation are distinct. A request can contain a valid name but lack a valid token, or it can contain a valid token but an invalid name. Keeping those cases separate makes the public behavior and tests easier to understand.

The test uses an HTML parser to locate the token by its field name. It does not depend on one brittle attribute ordering in the rendered HTML. This is a small example of testing a semantic contract rather than a serialization accident.

## Worked case: a complete valid form

The client first retrieves the form, retains the response cookies and extracts its token. It posts a valid name together with that token. The real form validation succeeds and returns status 201 with the validated name.

The response proves that this client request passed the configured server checks. It does not establish browser SameSite behavior, TLS or a deployed identity-provider flow. The owned application combines the relevant controls and provides separate browser/network acceptance.

For real deployments, the signing key, cookie settings, token lifetime and origin configuration must follow the deployment's trust boundary. The literal key here exists only to make the finite test fixture self-contained.

## Worked case: missing token versus invalid field

The next request submits a valid name without a token and receives 400. Another request submits the token but an empty name and also receives 400. Those equal status codes do not mean the failures had the same cause. The example exercises both checks deliberately.

Testing configurations sometimes disable CSRF to simplify unrelated tests. That can be useful for isolated business logic, but it would invalidate a test claiming to check CSRF. This fixture explicitly leaves the protection enabled and obtains a real token through the application.

## Worked example: a CSRF token is bound to one session

```python
import hashlib
import hmac
import secrets

SECRET = b"test-only-csrf-fixture"


def issue(session):
    session.setdefault("csrf_raw", secrets.token_hex(16))
    return hmac.new(SECRET, session["csrf_raw"].encode(), hashlib.sha256).hexdigest()


def accept(session, submitted):
    if "csrf_raw" not in session or not submitted:
        return False
    return hmac.compare_digest(issue(session), submitted)


victim, attacker = {}, {}
victim_token = issue(victim)
attacker_token = issue(attacker)
print(accept(victim, victim_token))
print(accept(victim, attacker_token))
print(accept(victim, None), accept({}, victim_token))
```

Expected output:

```text
True
False
False False
```

This is a simplified model of what Flask-WTF does behind `form.hidden_tag()`: a random value lives in the signed session cookie and the page embeds a keyed digest of it. The victim's own form submission passed. An attacker can load the site and obtain a perfectly valid token, but it is valid only for the attacker's session, so replaying it against the victim's session failed. A missing token and a session with no stored value were both rejected, matching the lesson's 400 for a POST without `csrf_token`. `hmac.compare_digest` avoids leaking how many leading characters matched through timing. The real extension also adds an expiry timestamp, so an old token copied from a cached page would eventually be refused even within the same session.

## Failure diagnosis

If a valid-looking token fails, inspect session continuity, signing-key consistency, expiration and the configured field/header name. A token copied from a different session may not satisfy the intended contract. If an entire test suite accepts forms without tokens, inspect its configuration before concluding that CSRF protection works.

A hidden input is not automatically secret or trustworthy. The browser client can inspect and modify it. Its usefulness comes from the server's validation and association with the appropriate context, not from hiding it visually in a form.

## Interview discussion

**Why does authentication not eliminate CSRF?** A browser may attach cookies automatically. Authentication identifies the credentials; CSRF controls help determine whether the state-changing request should be accepted under the application's browser-origin/session design.

**Should a CSRF test simply hard-code a token string?** Use the real framework's token generation and request flow unless the test is explicitly a lower-level unit test. A placeholder comparison does not qualify the framework integration.

## Next step

Use the authentication library's actual login and logout behavior, then apply object-level authorization to the identity it establishes.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python isolated
"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    from html.parser import HTMLParser

    from flask import Flask, render_template_string, request
    from flask_wtf import CSRFProtect, FlaskForm
    from wtforms import StringField
    from wtforms.validators import DataRequired, Length

    class Signup(FlaskForm):
        name = StringField("Name", validators=[DataRequired(), Length(max=40)])

    class Tokens(HTMLParser):
        token = None

        def handle_starttag(self, tag, attrs):
            fields = dict(attrs)
            if tag == "input" and fields.get("name") == "csrf_token":
                self.token = fields.get("value")

    app = Flask(__name__)
    app.config.update(TESTING=True, SECRET_KEY="test-only-csrf-fixture", WTF_CSRF_ENABLED=True)
    CSRFProtect(app)

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        form = Signup()
        if form.validate_on_submit():
            return {"name": form.name.data}, 201
        status = 400 if request.method == "POST" else 200
        return render_template_string(
            '<form method="post">{{ form.hidden_tag() }}'
            "{{ form.name.label }}{{ form.name }}</form>",
            form=form,
        ), status

    with app.test_client() as client:
        parser = Tokens()
        parser.feed(client.get("/signup").get_data(as_text=True))
        assert parser.token
        accepted = client.post("/signup", data={"name": "Ada", "csrf_token": parser.token})
        missing = client.post("/signup", data={"name": "Ada"})
        invalid = client.post("/signup", data={"name": "", "csrf_token": parser.token})
        assert accepted.status_code == 201 and accepted.json == {"name": "Ada"}
        assert missing.status_code == invalid.status_code == 400
    return {
        "validated_name": "Ada",
        "missing_csrf_status": 400,
        "invalid_field_status": 400,
        "actual_flask_wtf_checks": True,
        "browser_executed": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Flask documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
