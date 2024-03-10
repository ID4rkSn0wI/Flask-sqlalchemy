import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class Jobs(SqlAlchemyBase):
    __tablename__ = 'jobs'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    team_leader_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    team_leader = orm.relationship("User", foreign_keys=[team_leader_id])
    job = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    work_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    collaborators = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    categories = orm.relationship("Category",
                                  secondary="association",
                                  backref="jobs")

    @hybrid_property
    def categories_id(self):
        return ', '.join(list(map(lambda x: str(x.id), self.categories)))

    @hybrid_property
    def team_leader_initials(self):
        return f"{self.team_leader.surname} {self.team_leader.name}"

    def __repr__(self):
        return f"<Job> {self.job} {self.work_size} {self.team_leader.name} {self.team_leader.surname} {self.categories}"
