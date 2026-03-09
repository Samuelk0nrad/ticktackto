from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from backend.config import Config
from backend.engine import get_engine
from backend.model import Entity, Person, User

EXPECTED_TABLE_NAMES = [
    "entities",
    "persons",
    "users",
]


def test_engine_00():
    engine = get_engine()
    assert engine
    with engine.connect() as connection:
        inspector = inspect(connection)

        table_names = inspector.get_table_names()
        for expected_table_name in EXPECTED_TABLE_NAMES:
            assert expected_table_name in table_names


TEST_01_ENTITY_ID = 1
TEST_01_ENTITY_NAME = "Entity 1"
TEST_01_USER_NAME = "user1"
TEST_01_USER_PASSWORD_HASH = "hash"


def test_engine_01():
    _ = Config.get_instance()
    engine = get_engine()
    user_repr: str = ""
    with Session(bind=engine) as session:
        entity = Entity()
        entity.id = TEST_01_ENTITY_ID
        entity.name = TEST_01_ENTITY_NAME
        session.add(entity)
        session.commit()
        user = User()
        user.user_name = TEST_01_USER_NAME
        user.password_hash = TEST_01_USER_PASSWORD_HASH
        user.entity = entity
        session.add(user)
        session.commit()
        user_repr = repr(user)
    with Session(engine) as session:
        test_entities_rows = session.execute(text("select * from entities")).all()
        assert 1 == len(test_entities_rows)
        assert test_entities_rows[0][0] == TEST_01_ENTITY_ID
        assert test_entities_rows[0][1] == TEST_01_ENTITY_NAME
        test_users_rows = session.execute(text("select * from users")).all()
        assert 1 == len(test_users_rows)
        assert test_users_rows[0][0] == TEST_01_USER_NAME
        assert test_users_rows[0][1] == TEST_01_ENTITY_ID
        assert test_users_rows[0][2] == TEST_01_USER_PASSWORD_HASH

    assert (
        f"User(user_name='{TEST_01_USER_NAME}', password_hash='{TEST_01_USER_PASSWORD_HASH}', entity=Entity(id={TEST_01_ENTITY_ID}, name='{TEST_01_ENTITY_NAME}'))"
        == user_repr
    )


TEST_02_PERSON_ID = 2
TEST_02_PERSON_FIRST_NAME = "Jane"
TEST_02_PERSON_LAST_NAME = "Dow"

TEST_02_USER_NAME = "user2"
TEST_02_USER_PASSWORD_HASH = "hash2"


def test_engine_02():
    engine = get_engine()
    user_repr = ""
    with Session(engine) as session:
        person = Person()
        person.first_name = TEST_02_PERSON_FIRST_NAME
        person.last_name = TEST_02_PERSON_LAST_NAME
        person.id = TEST_02_PERSON_ID
        session.add(person)
        session.commit()
        user = User()
        user.user_name = TEST_02_USER_NAME
        user.password_hash = TEST_02_USER_PASSWORD_HASH
        user.entity = person
        session.add(user)
        session.commit()
        user_repr = repr(user)

    with Session(engine) as session:
        test_entities_rows = session.execute(text("select * from entities")).all()
        assert 1 == len(test_entities_rows)
        assert test_entities_rows[0][0] == TEST_02_PERSON_ID
        assert test_entities_rows[0][1] == TEST_02_PERSON_LAST_NAME
        test_persons_rows = session.execute(text("select * from persons")).all()
        assert 1 == len(test_persons_rows)
        assert test_persons_rows[0][0] == TEST_02_PERSON_ID
        assert test_persons_rows[0][1] == TEST_02_PERSON_FIRST_NAME

    assert (
        f"User(user_name='{TEST_02_USER_NAME}', password_hash='{TEST_02_USER_PASSWORD_HASH}', entity=Person(id={TEST_02_PERSON_ID}, last_name='{TEST_02_PERSON_LAST_NAME}', first_name='{TEST_02_PERSON_FIRST_NAME}'))"
        == user_repr
    )
