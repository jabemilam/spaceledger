from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Time, DateTime
from sqlalchemy.orm import relationship
from database import Base

# Table for users in the web app
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    #runs = relationship("Runs", back_populates="owner")

# Table for the information they'll be submitting
class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String)
    buy_location = Column(String)
    sell_location = Column(String)
    description = Column(String)
    expenditure = Column(Integer)
    sale = Column(Integer)
    profit = Column(Integer)
    run_time = Column(Time)
    run_date = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))

   # owner = relationship("Users", back_populates="runs")