import pytest

from app.database import Base, engine
from app.seed import seed


@pytest.fixture(scope="session", autouse=True)
def database_schema():
    Base.metadata.create_all(engine)
    seed()
    yield
    Base.metadata.drop_all(engine)
