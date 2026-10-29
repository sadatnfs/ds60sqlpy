"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    from django.conf import settings

    settings.configure(
        SECRET_KEY="synthetic-local-fixture",
        INSTALLED_APPS=[],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    )
    import django

    django.setup()
    from django import forms
    from django.db import connection, models

    class Note(models.Model):
        title = models.CharField(max_length=40)
        owner = models.CharField(max_length=20)

        class Meta:
            app_label = "webfixture"

    class NoteForm(forms.ModelForm):
        class Meta:
            model = Note
            fields = ["title"]

        def clean_title(self):
            value = self.cleaned_data["title"].strip()
            if len(value) < 3:
                raise forms.ValidationError("Use at least three characters")
            return value

    with connection.schema_editor() as editor:
        editor.create_model(Note)
    form = NoteForm({"title": "  Review  ", "owner": "attacker"})
    assert form.is_valid()
    note = form.save(commit=False)
    note.owner = "authenticated-user"
    note.save()
    assert (note.title, note.owner) == ("Review", "authenticated-user")
    invalid = NoteForm({"title": " x "})
    assert not invalid.is_valid() and "title" in invalid.errors
    assert Note.objects.count() == 1
    assert "owner" not in form.fields
    connection.close()
    return {
        "cleaned_title": note.title,
        "owner_from_server": note.owner,
        "model_form_ignores_unlisted_input": (
            "validate unknown keys separately if your API requires refusal"
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
