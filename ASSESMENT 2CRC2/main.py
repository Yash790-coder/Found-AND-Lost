from contextlib import asynccontextmanager
from enum import Enum

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import field_validator
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Status(str, Enum):
    LOST = "Lost"
    FOUND = "Found"
    RETURNED = "Returned"


class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=5, max_length=2000)
    category: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=200)
    reported_by: str = Field(min_length=1, max_length=120)
    status: Status = Status.LOST

    @field_validator("title", "description", "category", "location", "reported_by")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must contain meaningful text")
        return value.strip()


class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=5, max_length=2000)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    location: str | None = Field(default=None, min_length=1, max_length=200)
    reported_by: str | None = Field(default=None, min_length=1, max_length=120)
    status: Status | None = None


sqlite_url = "sqlite:///./lost_and_found.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Campus Lost & Found API",
    description="REST API for reporting and managing lost and found campus items.",
    version="1.0.0",
    lifespan=lifespan,
)


def get_session():
    with Session(engine) as session:
        yield session


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, session: Session = Depends(get_session)):
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@app.get("/items", response_model=list[Item])
def read_items(session: Session = Depends(get_session)):
    return session.exec(select(Item)).all()


@app.get("/items/status/{item_status}", response_model=list[Item])
def read_items_by_status(item_status: Status, session: Session = Depends(get_session)):
    return session.exec(select(Item).where(Item.status == item_status)).all()


@app.get("/items/category/{category}", response_model=list[Item])
def read_items_by_category(category: str, session: Session = Depends(get_session)):
    return session.exec(select(Item).where(Item.category == category)).all()


@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{item_id}", response_model=Item)
def update_item(
    item_id: int,
    item_update: ItemUpdate,
    session: Session = Depends(get_session),
):
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_update.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    session.delete(item)
    session.commit()
