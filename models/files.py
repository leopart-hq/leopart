from sqlalchemy import Column, Integer, String
from .base import Base


class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    uuid = Column(String)
    repo_id = Column(String)

    def __repr__(self):
        return f"<File(id='{self.id}', url='{self.url}', uuid='{self.uuid}', repo_id='{self.repo_id}')>"

    def __str__(self):
        return f"<File(id='{self.id}', url='{self.url}', uuid='{self.uuid}', repo_id='{self.repo_id}')>"
