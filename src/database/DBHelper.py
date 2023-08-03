from sqlalchemy import create_engine, Column, Integer, String, inspect, ForeignKey, Boolean, Text, TIMESTAMP
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from sqlalchemy.future import select
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy import func
from threading import Lock
from datetime import datetime
from contextlib import contextmanager
from typing import Generator
from tqdm import *
import time
import json


Base = declarative_base()

class DBHelper:
    def __init__(self, data_base_name: str):
        self.__engine = create_engine(f'sqlite:///{data_base_name}', poolclass=NullPool)
        self.__Session: Session = sessionmaker(bind=self.__engine)
        # self.__session = self.__Session()
        self.lock = Lock()
        Base.metadata.create_all(self.__engine)

    @property
    def engine(self):
        return self.__engine

    def insert_raw_data(self, data: list):
        d = []
        with self.__Session() as session:
            for row in tqdm(data, total=len(data)):
                object_row = RawData(text=row)
                d.append(object_row)
            session.add_all(d)
            session.commit()

    @contextmanager
    def scoped_session(self) -> Generator[Session, None, None]:
        session = self.__Session()
        self.lock.acquire()
        try:
            yield session
        except Exception as e:
            session.rollback()
            print(f"<scoped_session>: {e}")
        finally:
            session.commit()
            self.lock.release()
            session.close()

    def insert_result_data(self, data: list[tuple], Table: Base):
        print("Inserting...")
        # with self.scoped_session() as session:
        # session = self.__Session()
        with self.__Session() as session:
            with session.no_autoflush:
                with session.begin():
                    for row_id, data_dict in tqdm(data, total=len(data)):
                        values = data_dict["simple_forms"]
                        for value in values:
                            object_row = Table(
                                text=value['simple_form'],
                                tag=value['tag'],
                                raw_data_id=row_id,
                            )
                            session.add(object_row)
                        self.update_data_flag(session, row_id)
            session.commit()
                    # try:
                    #     session.add(object_row)
                    #     self.update_data_flag(session, row_id)
                    # except:
                    #     session.rollback()
                    # finally:
                    #     session.commit()
                    #     session.close()

    # def insert_bad_request_data(self, data: list[tuple]):
    #     d = []
    #     with self.__Session() as session:
    #         # list_object_rows = []
    #         for tuple_ in tqdm(data, total=len(data)):
    #             id = tuple_[0]
    #             text = tuple_[1]
    #             object_row = BadRequestData(text=text, raw_data_id=id)
    #             d.append(object_row)
    #             # d.extend(list_object_rows)  
    #         session.add_all(d)
    #         session.commit()

    # def delete_raw_data(self, id):
    #     data = self.__session.query(RawData).filter(RawData.id == id).first()
    #     self.__session.delete(data)
    #     self.__session.commit()

    # def delete_result_data(self, id):
    #     data = self.__session.query(ResultData).filter(ResultData.id == id).first()
    #     self.__session.delete(data)
    #     self.__session.commit()

    def get_raw_data(self, num, used: bool = False) -> list[tuple]:
        # with self.__Session() as session:
        #     # with session.begin():
        #     stmt = select(RawData).filter(RawData.used == used).limit(num)
        #     data = session.scalars(stmt)
        data = self.__Session().query(RawData).filter(RawData.used == used).limit(num).all()
        return [(d.id, d.text) for d in data]

    def update_data_flag(self, session: Session, row_id: int, commit: bool = False):
        # session.query(RawData).filter(RawData.id == row_id).update({"used": True})
        update_row: RawData = session.query(RawData).get(row_id)
        update_row.used = True

        if commit:
            session.commit()

    def add_bind_session(
        self, 
        email: str,
        password: str,
        second_email: str = None,
        second_password: str = None,
        cookie: str = None,
        user_agent: str = None,
        ):
        with self.__Session() as session:
            obj = BingCookie(
                email=email,
                password=password,
                second_email=second_email,
                second_password=second_password,
                cookie=json.dumps(cookie),
                user_agent=user_agent,
                )
            session.add(obj)
            session.commit()

    def update_bing_cookie(
        self,
        email: str,
        cookie: str,
        ):
        update = self.__Session().query(
            BingCookie
        ).filter(
            BingCookie.email == email
        ).update(
            {
                "cookie": json.dumps(cookie), 
                "timestamp": func.strftime("%s", datetime.utcnow()),
            }
        )
        self.__Session().commit()

    def update_user_agent(
        self,
        email: str,
        user_agent: str,
        ):
        update = self.__Session().query(
            BingCookie
        ).filter(
            BingCookie.email == email
        ).update(
            {
                "user_agent": user_agent, 
            }
        )
        self.__Session().commit()

    def get_fresh_cookies(
        self,
        # email: str,
        ) -> list:
        query: BingCookie
        query = self.__Session().query(
            BingCookie
        ).filter(
            # BingCookie.email == email,
            BingCookie.timestamp > (func.strftime("%s", datetime.utcnow()) - 1500)
        ).all()
        if query:
            cookies = [json.loads(q.cookie) for q in query if q.cookie]
            if len(cookies) > 0:
                return cookies
        return

    def get_fresh_cookie(
        self,
        email: str,
        ) -> list:
        query: BingCookie
        query = self.__Session().query(
            BingCookie
        ).filter(
            BingCookie.email == email,
            BingCookie.timestamp > (func.strftime("%s", datetime.utcnow()) - 1500)
        ).first()
        if query:
            if query.cookie:
                cookies = json.loads(query.cookie)
                if cookies:
                    if len(cookies) > 0:
                        return cookies
        return
    
    def get_cookie(
        self,
        email: str,
    ):
        query: BingCookie = self.__Session().query(
            BingCookie
        ).filter(
            BingCookie.email == email,
        ).first()
        if query:
            if query.cookie:
                cookies = json.loads(query.cookie)
                if cookies:
                    if len(cookies) > 0:
                        return cookies
        return

    def get_emails(
        self,
        ) -> list[str]:
        query = self.__Session().query(BingCookie).all()
        if query:
            return [email.email for email in query]
        return

    def get_auth_data(
        self,
        email: str) -> dict:
        if email:
            q = self.__Session().query(
                BingCookie
            ).filter(
                BingCookie.email == email,
            ).first()
        else:
            q = self.__Session().query(
                BingCookie
            ).all()
        if q:
            q: BingCookie
            dct = {
                "email": q.email,
                "password": q.password,
                "second_email": q.second_email,
                "second_password": q.second_password,
                "user_agent": q.user_agent,
            }
            return dct
        return
    
    def get_user_agent(
        self,
        email: str
    ):
        query: BingCookie = self.__Session().query(
            BingCookie
        ).filter(
            BingCookie.email == email
        ).first()
        if query:
            return query.user_agent
        return

    def get_stale_cookies(self) -> list[dict]:
        query = self.__Session().query(
            BingCookie
        ).filter(
            BingCookie.timestamp < (func.strftime("%s", datetime.utcnow()) - 1500)
        ).all()
        stale = []
        for q in query:
            q: BingCookie
            d = {}
            d["email"] = q.email
            d["password"] = q.password
            d["second_email"] = q.second_email
            d["second_password"] = q.second_password
            if q.cookie:
                d["cookie"] = json.loads(q.cookie)
            stale.append(d)
        if len(stale) > 0:
            return stale
        return

class RawData(Base):
    __tablename__ = 'raw_data'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    used = Column(Boolean, default=False)
    data = relationship('ResultData', back_populates='result_data')
    bing_data = relationship('BingData', back_populates='bing_data')

class ResultData(Base):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    tag = Column(String)
    raw_data_id = Column(Integer, ForeignKey('raw_data.id'))
    result_data = relationship('RawData', back_populates='data')

class BingData(Base):
    __tablename__ = 'bing_result'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    tag = Column(String)
    raw_data_id = Column(Integer, ForeignKey('raw_data.id'))
    bing_data = relationship('RawData', back_populates='bing_data')

class BadRequestData(Base):
    __tablename__ = 'bad_request'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    used = Column(Boolean, default=False)
    raw_data_id = Column(Integer, ForeignKey('raw_data.id'))

class BingCookie(Base):
    __tablename__ = 'cookies_bing_session'
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    second_email = Column(String)
    second_password = Column(String)
    user_agent = Column(String)
    cookie = Column(Text)
    timestamp = Column(Integer, default=func.strftime("%s", datetime.utcnow()))
