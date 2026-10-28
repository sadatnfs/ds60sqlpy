"""Strict structural validation and directional semantic compatibility."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class DeliveryV1(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    delivery_id: str = Field(min_length=1, pattern=r".*\S.*")
    packages: int = Field(ge=1)


class DeliveryV2(DeliveryV1):
    priority: Literal["normal", "urgent"] | None = None


def example_one():
    old_record = {"delivery_id": "A", "packages": 2}
    new_reader = DeliveryV2.model_validate(old_record)
    assert new_reader.packages == 2 and new_reader.priority is None
    try:
        DeliveryV1.model_validate({**old_record, "priority": "urgent"})
    except ValidationError as error:
        assert any(item["type"] == "extra_forbidden" for item in error.errors())
    else:
        raise AssertionError("This strict old reader must reject the extra field")
    return {
        "new_reader_accepts_old_record": new_reader.model_dump(),
        "old_reader_accepts_new_field": False,
    }


def example_two():
    class UnqualifiedDistance(BaseModel):
        distance: float

    class KilometerDistance(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")
        distance: float = Field(ge=0)
        unit: Literal["km"]

    bare = UnqualifiedDistance.model_validate({"distance": 1000})
    assert bare.distance == 1000.0
    try:
        KilometerDistance.model_validate({"distance": 1000.0, "unit": "m"})
    except ValidationError:
        rejected_wrong_unit = True
    else:
        raise AssertionError("The receiver declared kilometers, not meters")
    corrected = KilometerDistance.model_validate({"distance": 1.0, "unit": "km"})
    try:
        DeliveryV1.model_validate({"delivery_id": "A", "packages": "2"})
    except ValidationError:
        rejected_implicit_cast = True
    else:
        raise AssertionError("Strict validation must not hide an undeclared conversion")
    return {
        "unqualified_number_was_structurally_valid": bare.distance,
        "wrong_unit_rejected": rejected_wrong_unit,
        "explicit_conversion": corrected.model_dump(),
        "implicit_cast_rejected": rejected_implicit_cast,
    }


def main():
    print("Compatibility has a direction:", example_one())
    print("A type alone does not specify meaning:", example_two())


if __name__ == "__main__":
    main()
