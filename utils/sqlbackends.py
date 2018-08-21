# -*- coding: utf-8 -*-

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import loggererror as logger

mysql_client = create_engine(
    "mysql+pymysql://zww:msbasic31@" "192.168.188.114:3306/bailu?charset=utf8",
    encoding="utf-8",
)

session_sql = sessionmaker(bind=mysql_client)


@contextmanager
def session_scope():
    session = session_sql()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error('there is an error when in session {}'.format(e), exc_info=True)
        raise
    finally:
        session.close()
