import os
import time

from sqlalchemy.exc import StatementError
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_PASSWORD = os.getenv("DATA_BASE_PASSWORD")
DATABASE_ENDPOINT = os.getenv("DATA_BASE_ENDPOINT")
DATABASE_NAME = os.getenv("DATA_BASE_NAME")
CLUSTER_ARN = os.getenv("RDS_ARN")
SECRET_ARN = os.getenv("SECRET_ARN")
RETRY_SEC = 5

engine = create_engine(
    f"mysql+auroradataapi://admin:{DATABASE_PASSWORD}@{DATABASE_ENDPOINT}/{DATABASE_NAME}",
    pool_recycle=180,
    echo=True,
    connect_args=dict(aurora_cluster_arn=CLUSTER_ARN, secret_arn=SECRET_ARN),
)

db_session = scoped_session(
    sessionmaker(autocommit=True, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from application.models import User, RoleUser, Role, Files

    while True:
        try:
            Base.metadata.create_all(bind=engine)
            break
        except StatementError:
            print(f'Database initializing, retry in {RETRY_SEC} seconds.')
            time.sleep(RETRY_SEC)
