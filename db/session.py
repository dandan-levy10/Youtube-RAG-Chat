from sqlmodel import Session, SQLModel, create_engine

from app.core.config import DATABASE_URL

engine = create_engine(url= DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session