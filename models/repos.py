from sqlalchemy import Column, Integer, String
from .base import Base


class Repo(Base):
    __tablename__ = 'repos'
    id = Column(Integer, primary_key=True)
    repo_url = Column(String)
    repo_uuid = Column(String)
    description = Column(String)
    name = Column(String)
    license = Column(String)
    license_url = Column(String)
    readme = Column(String)
    readme_url = Column(String)
    forks = Column(Integer)
    stars = Column(Integer)

    def __repr__(self):
        return f"<Repo(id={self.id}, repo_url={self.repo_url}, repo_uuid={self.repo_uuid}, description=" \
               f"{self.description}, name={self.name}, license={self.license}, license_url={self.license_url}," \
               f"readme={self.readme}, readme_url={self.repo_url}, forks={self.forks}, stars={self.stars})>"

    def __str__(self):
        return f"<Repo(id={self.id}, repo_url={self.repo_url}, repo_uuid={self.repo_uuid}, description=" \
               f"{self.description}, name={self.name}, license={self.license}, license_url={self.license_url}," \
               f"readme={self.readme}, readme_url={self.repo_url}, forks={self.forks}, stars={self.stars})>"
