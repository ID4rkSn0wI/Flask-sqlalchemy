import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class Department(SqlAlchemyBase):
    __tablename__ = 'departments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    chief = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    members = relationship("User", back_populates="department")

    @hybrid_property
    def members_id(self):
        return ', '.join(list(map(lambda x: str(x.id), self.members)))

    def __repr__(self):
        return f"<Department> {self.id} {self.title} {self.members}"
