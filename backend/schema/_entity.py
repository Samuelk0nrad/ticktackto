from pydantic import BaseModel


class EntityBase(BaseModel):
    name: str


class EntityFull(EntityBase):
    id: int
