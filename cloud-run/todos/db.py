from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base


#SQLALCHEMY_DATABASE_URI = "sqlite:///./test.db"
#SQLALCHEMY_DATABASE_URI = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URI = "mysql://user:password@mysqlserver/db?charset=utf8"

engine = create_engine(
#    SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}, echo=True
    SQLALCHEMY_DATABASE_URI
)

Base = declarative_base()

# Todoテーブルの定義
class Todo(Base):
    __tablename__ = 'todos'
    id = Column('id', Integer, primary_key = True)
    title = Column('title', String(200))
    done = Column('done', Boolean, default=False)

# テーブル作成
Base.metadata.create_all(bind=engine)

