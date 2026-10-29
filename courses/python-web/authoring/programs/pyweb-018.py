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
