# pyweb-051: Django forms, ModelForms and field ownership

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-050`.

## Starting point and result

Django forms validate user input and produce cleaned values. ModelForms connect a selected form surface to a model, but that connection must not expose every model field automatically. This chapter validates a title while assigning ownership from server context, and shows how extra submitted fields differ from explicitly declared form fields.

## Key terms

- **ModelForm:** A Django form generated from a model whose `Meta.fields` list selects exactly which fields the user may edit.
- **cleaned_data:** The dictionary of validated and normalized values that `is_valid()` produces when a form has no errors.
- **clean_title:** A field-specific clean method that normalizes and checks one value beyond the model's basic type and length rules.
- **commit=False:** A `save()` option that builds the model instance without writing it, so the view can set trusted fields such as owner first.
- **Undeclared input:** Submitted keys that are not form fields; Django forms ignore them, so strict rejection of unknown keys needs explicit code.

## Mechanism: the form defines writable input

A ModelForm Meta.fields list selects the fields the user may edit. The model can contain additional fields such as owner that the form intentionally excludes. Custom clean_title logic can normalize whitespace and enforce a domain rule beyond the model's basic type and length.

Calling is_valid populates cleaned_data or errors. Save with commit=False constructs the model instance without immediately writing it. The application can then assign trusted fields and save deliberately. This is useful for owner identity, tenant, audit information or other values that should not come from client-controlled form data.

Django forms ordinarily ignore undeclared input keys rather than rejecting them as unknown fields. That behavior is appropriate in many HTML form flows, but an API requiring strict unknown-key refusal must add that policy explicitly. The lesson reports this distinction instead of suggesting that a fields list proves the entire raw input was rejected.

## Worked case: normalize a title and assign the owner

The valid form includes whitespace around its title and a hostile-looking owner field. Validation cleans the title to Review. The program builds the model with commit=False, assigns the authenticated-user fixture identity on the server and saves it.

The stored row contains the cleaned title and server-selected owner. The owner key supplied by the client did not become a writable form field. The program also asserts that owner is absent from the form's field collection, making the intended edit surface inspectable.

This pattern does not itself authenticate the user. The fixture supplies a known identity so the field-ownership mechanism remains clear. Later authentication chapters establish the principal, and the integrated walkthrough combines that principal with the model write.

## Worked case: refuse an invalid title without a write

A second form contains a title that becomes too short after stripping whitespace. Validation fails with a title error, and no save occurs. The final model count remains one, proving that the invalid form did not create another row.

Normalization order matters. Checking length before trimming could admit a value whose meaningful content is too short. Conversely, aggressive normalization can change valid user intent. Define the domain's intended representation and test the meaningful boundary cases.

For an existing object, the application must also authorize which instance is being edited. Excluding owner from the form does not stop a caller from selecting another user's object if the view loads that object without an ownership predicate. Input field control and object selection are separate authorization boundaries.

## Worked example: ignoring unlisted fields versus refusing them

```python
ALLOWED = {"title"}


def bind(payload, strict):
    unknown = sorted(set(payload) - ALLOWED)
    if strict and unknown:
        return {"errors": {"__all__": f"unexpected fields: {unknown}"}}
    title = payload.get("title", "").strip()
    if len(title) < 3:
        return {"errors": {"title": "Use at least three characters"}}
    return {"title": title, "owner": "authenticated-user"}


attack = {"title": "  Review  ", "owner": "attacker"}
print(bind(attack, strict=False))
print(bind(attack, strict=True))
print(bind({"title": " x "}, strict=False))
```

Expected output:

```text
{'title': 'Review', 'owner': 'authenticated-user'}
{'errors': {'__all__': "unexpected fields: ['owner']"}}
{'errors': {'title': 'Use at least three characters'}}
```

The non-strict branch behaves like the lesson's `NoteForm` with `fields = ["title"]`: the forged `owner` key is simply never read, and the view sets the owner from the server side after `save(commit=False)`. That is safe, but the client gets no signal that its request carried a field the server ignored. The strict branch adds the separate unknown-key check that the program's return value mentions, which is the right choice for a JSON API whose contract says extra keys are errors. Both branches strip whitespace before the length check, which is why `" x "` fails while `" Review "` passes.

## Failure diagnosis and discussion

**Why use commit=False?** It allows trusted server-owned fields to be assigned before the first write. It is not a replacement for a transaction when several related writes must commit together.

**Does Meta.fields reject an attacker-supplied owner key?** It excludes owner from the form's writable fields, but the raw extra key is normally ignored. A strict API can reject unexpected keys separately and should test that behavior.

If a form saves an unexpected owner, inspect instance construction and assignment order. If a validation error still changes storage, inspect whether a write occurred before is_valid. Continue with class-based views, where reusable machinery can reduce repetition while requiring careful dispatch and permission composition.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)
