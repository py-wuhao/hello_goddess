from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, BigInteger
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:123456@localhost:3306/sport?charset=utf8mb4')
Base = declarative_base()
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

class Sport(Base):
    __tablename__ = 'sport_info'

    id = Column(BigInteger, primary_key=True)
    friend_id = Column(Integer,index=True)
    points = Column(Integer)
    timestamp = Column(BigInteger)


class Friend(Base):
    __tablename__ = 'friend_info'

    id = Column(BigInteger, primary_key=True)
    nick_name = Column(String(32), index=True)
    qq = Column(BigInteger)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
