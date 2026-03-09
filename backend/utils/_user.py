import os
import sys

from sqlalchemy.orm import Session

from BACKEND_NAME_PLACEHOLDER.engine import get_engine
from BACKEND_NAME_PLACEHOLDER.model import Entity, Person, User


def user_main():
    try:
        config_file_name = sys.argv[1]
        user_name = sys.argv[2]
        password_hash = sys.argv[3]
        name = sys.argv[4]
        first_name = None
        try:
            first_name = sys.argv[5]
        except IndexError:
            pass
        print(
            f"config: {config_file_name} user_name: {user_name} password: {password_hash} name: {name} first_name: {first_name}"
        )
        engine = get_engine(config_file_name)
        with Session(engine) as session:
            user = User()
            user.user_name = user_name
            user.password_hash = password_hash
            if first_name:
                person = Person()
                person.first_name = first_name
                person.last_name = name
                user.entity = person
                session.add(person)
            else:
                entity = Entity()
                entity.name = name
                user.entity = entity
                session.add(entity)
            session.add(user)
            session.commit()
            print("Done")

    except IndexError:
        print(
            f"Usage: {os.path.basename(sys.argv[0])} config_file_name user_name password_hash name [first_name]"
        )
