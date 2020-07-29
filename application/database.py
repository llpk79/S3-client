import os
import time

from sqlalchemy.exc import StatementError
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

database_password = os.getenv("DATA_BASE_PASSWORD")
database_endpoint = os.getenv("DATA_BASE_ENDPOINT")
database_name = os.getenv("DATA_BASE_NAME")
cluster_arn = os.getenv("RDS_ARN")
secret_arn = os.getenv("SECRET_ARN")


engine = create_engine(
    f"mysql+auroradataapi://admin:{database_password}@{database_endpoint}/{database_name}",
    pool_recycle=180,
    echo=True,
    connect_args=dict(aurora_cluster_arn=cluster_arn, secret_arn=secret_arn),
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
            time.sleep(5)
