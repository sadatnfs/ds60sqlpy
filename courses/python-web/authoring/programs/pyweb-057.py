"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    from django.conf import settings

    settings.configure(
        SECRET_KEY="synthetic-local-fixture",
        ROOT_URLCONF=__name__,
        REST_FRAMEWORK={"UNAUTHENTICATED_USER": None, "DEFAULT_AUTHENTICATION_CLASSES": []},
    )
    import django

    django.setup()
    from rest_framework import serializers, status, viewsets
    from rest_framework.response import Response
    from rest_framework.routers import SimpleRouter
    from rest_framework.test import APIClient

    class NoteSerializer(serializers.Serializer):
        identifier = serializers.IntegerField(read_only=True)
        title = serializers.CharField(max_length=40)

        def validate_title(self, value):
            if len(value.strip()) < 3:
                raise serializers.ValidationError("Use at least three characters")
            return value.strip()

    records = []

    class Notes(viewsets.ViewSet):
        def list(self, request):
            return Response(NoteSerializer(records, many=True).data)

        def create(self, request):
            serializer = NoteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            row = {"identifier": len(records) + 1, **serializer.validated_data}
            records.append(row)
            return Response(NoteSerializer(row).data, status=status.HTTP_201_CREATED)

    router = SimpleRouter()
    router.register("notes", Notes, basename="note")
    global urlpatterns
    urlpatterns = router.urls
    client = APIClient()
    assert client.post(
        "/notes/", {"title": "  Plan  ", "identifier": 999}, format="json"
    ).json() == {"identifier": 1, "title": "Plan"}
    assert client.post("/notes/", {"title": "x"}, format="json").status_code == 400
    assert client.get("/notes/").json() == [{"identifier": 1, "title": "Plan"}]
    return {
        "serializer_and_router": True,
        "read_only_field_ignored": True,
        "storage": "bounded in-memory fixture",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
