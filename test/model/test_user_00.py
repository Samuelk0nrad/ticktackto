from backend.model import Entity, Person, User

ENTITY_ID = 1
ENTITY_NAME = "Entity 1"

USER_USER_NAME = "user"
USER_PASSWORD_HASH = "password_hash"

PERSON_ID = 3
PERSON_FIRST_NAME = "John"
PERSON_LAST_NAME = "Doe"


def test_user_00() -> None:
    entity = Entity()
    entity.id = ENTITY_ID
    entity.name = ENTITY_NAME

    user = User()
    user.user_name = USER_USER_NAME
    user.password_hash = USER_PASSWORD_HASH

    user.entity = entity

    user_copy = eval(repr(user))  # pyright: ignore [reportAny]

    assert f"{user_copy}" == f"{user}"

    assert (
        f"User(user_name='{USER_USER_NAME}', password_hash='{USER_PASSWORD_HASH}', entity=Entity(id={ENTITY_ID}, name='{ENTITY_NAME}'))"
        == repr(user)
    )


def test_user_01() -> None:
    entity = Person()
    entity.id = PERSON_ID
    entity.first_name = PERSON_FIRST_NAME
    entity.name = PERSON_LAST_NAME

    user = User()
    user.user_name = USER_USER_NAME
    user.password_hash = USER_PASSWORD_HASH

    user.entity = entity

    user_copy = eval(repr(user))  # pyright: ignore [reportAny]

    assert f"{user_copy}" == f"{user}"

    assert (
        f"User(user_name='{USER_USER_NAME}', password_hash='{USER_PASSWORD_HASH}', entity=Person(id={PERSON_ID}, last_name='{PERSON_LAST_NAME}', first_name='{PERSON_FIRST_NAME}'))"
        == repr(user)
    )
