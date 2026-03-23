from sqlalchemy import Column, Integer, String, JSON
from database import Base

class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    dob = Column(String)
    schedule = Column(JSON)