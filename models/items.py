from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    module = Column(String)
    description = Column(String)
    tags = Column(String)
    reference = Column(String)
    value = Column(String)
    part_id = Column(String, ForeignKey("parts.id"))
    file_id = Column(String, ForeignKey('files.id'))

    def __repr__(self):
        return f"<Item(id={self.id}, uuid={self.uuid}, module={self.module}, description={self.description}, " \
               f"file_id={self.file_id}, part_id={self.part_id}>"

    def __str__(self):
        return f"<Item(id={self.id}, uuid={self.uuid}, module={self.module}, description={self.description}, " \
               f"file_id={self.file_id}, part_id={self.part_id}>"
