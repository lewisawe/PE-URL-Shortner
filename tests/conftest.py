import os
import pytest

os.environ["DATABASE_NAME"] = "hackathon_test"

from app import create_app
from app.database import db
from app.models import User, Url, Event


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create tables once for the test session"""
    app = create_app()
    with app.app_context():
        db.drop_tables([Event, Url, User], safe=True)
        db.create_tables([User, Url, Event])
    yield
    with app.app_context():
        db.drop_tables([Event, Url, User], safe=True)


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_user(app):
    from datetime import datetime
    import uuid
    with app.app_context():
        user = User.create(
            username=f"testuser_{uuid.uuid4().hex[:8]}",
            email=f"test_{uuid.uuid4().hex[:8]}@test.com",
            created_at=datetime.now()
        )
        yield user
