from sqlalchemy import *
from config import host, port, database, user, password
from sqlalchemy import create_engine
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class DbCluj:
    def __init__(self):
        self.conn_str = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(self.conn_str)
        self.Session = sessionmaker(bind=self.engine)
        self.base = declarative_base()
        self.metadata = MetaData(self.engine)

        self.real_estate_cluj = Table('real_estate_cluj', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('location', String),
                                Column('rooms_num', Integer),
                                Column('dimension', Float),
                                Column('level', String),
                                Column('architecture', String),
                                Column('price', Float),
                                Column('currency', String),
                                Column('scraped_date', Date))

    def insert_cluj_estate_record(self, list_record):
        if len(list_record) == 8:
            insert_record = self.real_estate_cluj.insert().values(
                location = list_record[0],
                rooms_num = list_record[1],
                dimension = list_record[2],
                level = list_record[3],
                architecture = list_record[4],
                price = list_record[5],
                currency = list_record[6],
                scraped_date = list_record[7]
                )
            conn = self.engine.connect()
            conn.execute(insert_record)


