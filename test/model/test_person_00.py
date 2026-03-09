from backend.model import Person

TEST_ID_01 = 1
TEST_FIRST_NAME_01 = "John"
TEST_LAST_NAME_01 = "Doe"

REPR_01 = f"Person(id={TEST_ID_01}, last_name='{TEST_LAST_NAME_01}', first_name='{TEST_FIRST_NAME_01}')"
STR_01 = REPR_01


def test_entity_00() -> None:
    entity = Person()
    entity.id = TEST_ID_01
    entity.name = TEST_LAST_NAME_01
    entity.first_name = TEST_FIRST_NAME_01
    entity_copy: Person = eval(repr(entity))  # pyright: ignore [reportAny]
    assert type(entity_copy) == Person
    assert str(entity) == str(entity_copy)
    assert REPR_01 == repr(entity)
    assert STR_01 == str(entity)
