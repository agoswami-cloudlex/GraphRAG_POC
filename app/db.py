from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
import os

import pathlib
project_root = pathlib.Path(__file__).parent.parent.resolve()
db_path = project_root / "app.db"
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
	SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
	with Session(engine) as session:
		yield session
