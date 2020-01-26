import uuid as uuid
from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base


class Part(Base):
    __tablename__ = 'parts'
    id = Column(Integer, primary_key=True)
    # uuid = Column(String, default=str(uuid.uuid4()))
    description = Column(String)
    manufacturer = Column(String)
    aisler_id = Column(String, unique=True)
    mpn = Column(String)
    datasheet = Column(String)

    def __repr__(self):
        return f"<Part(id='{self.id}', description='{self.description}', manufacturer='{self.manufacturer}', " \
               f"aisler_id='{self.aisler_id}', mpn='{self.mpn}', datasheet='{self.datasheet}')>"

    def __str__(self):
        return f"<Part(id='{self.id}', description='{self.description}', manufacturer='{self.manufacturer}', " \
               f"aisler_id='{self.aisler_id}', mpn='{self.mpn}', datasheet='{self.datasheet}')>"
