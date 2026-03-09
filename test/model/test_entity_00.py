from backend.model import Entity

TEST_ID_01 = 1
TEST_NAME_01 = "TEST ENTITY 1"
REPR_01 = f"Entity(id={TEST_ID_01}, name='{TEST_NAME_01}')"
STR_01 = f"Entity(id={TEST_ID_01}, name='{TEST_NAME_01}')"


def test_entity_00() -> None:
    entity = Entity()
    entity.id = TEST_ID_01
    entity.name = TEST_NAME_01
    entity_copy: Entity = eval(repr(entity))  # pyright: ignore [reportAny]
    assert type(entity_copy) == Entity
    assert str(entity) == str(entity_copy)
    assert REPR_01 == repr(entity)
    assert STR_01 == str(entity)
