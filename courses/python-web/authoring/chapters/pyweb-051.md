## Starting point and result

Django forms validate user input and produce cleaned values. ModelForms connect a selected form surface to a model, but that connection must not expose every model field automatically. This chapter validates a title while assigning ownership from server context, and shows how extra submitted fields differ from explicitly declared form fields.

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

## Failure diagnosis and discussion

**Why use commit=False?** It allows trusted server-owned fields to be assigned before the first write. It is not a replacement for a transaction when several related writes must commit together.

**Does Meta.fields reject an attacker-supplied owner key?** It excludes owner from the form's writable fields, but the raw extra key is normally ignored. A strict API can reject unexpected keys separately and should test that behavior.

If a form saves an unexpected owner, inspect instance construction and assignment order. If a validation error still changes storage, inspect whether a write occurred before is_valid. Continue with class-based views, where reusable machinery can reduce repetition while requiring careful dispatch and permission composition.
