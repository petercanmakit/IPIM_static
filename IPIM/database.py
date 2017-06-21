from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

def dbConnect(DATABASEURI):
    '''
    connect to database by DATABASEURI
    return an sqlalchemy engine
    '''
    engine = create_engine(DATABASEURI)
    return engine
