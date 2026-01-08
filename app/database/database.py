from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

DATABASE_URL = "postgresql://postgres:Admin@localhost:5432/Employee"

engine = create_engine(DATABASE_URL)

sessionmaker = sessionmaker(automcommit = False, autoflush= False, bind= engine)

Base = declarative_base()
