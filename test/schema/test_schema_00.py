from backend.schema import EntityBase, EntityFull


def test_entity_00():
    entity_base = EntityBase(name="Ulmer")

    entity_base_copy: EntityBase = eval(  #  pyright: ignore [reportAny]
        repr(entity_base)
    )
    assert entity_base_copy.name == entity_base.name

    entity: EntityFull = EntityFull(id=1, name="Fritz")

    entity_copy: EntityFull = eval(repr(entity))  #  pyright: ignore [reportAny]

    assert entity_copy == entity

def test_fail():
    assert True
