from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select


load_dotenv()

class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


db_url = os.getenv("DATABASE_URL")

if db_url is None:
    raise ValueError("DB_URL is not set in the environment")

engine = create_engine(db_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app : FastAPI = FastAPI(lifespan=lifespan)


@app.post("/todo/")
def create_todo(Todo: Todo):
    with Session(engine) as session:
        session.add(Todo)
        session.commit()
        session.refresh(Todo)
        return Todo


@app.get("/todo/")
def read_todo():
    with Session(engine) as session:
        Todo = session.exec(select(Todo)).all()
        return Todo
    