import csv
import json
from datetime import datetime

from peewee import chunked

from app.database import db
from app.models import Event, Url, User


def parse_datetime(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def load_users(filepath="users.csv"):
    with open(filepath) as f:
        rows = list(csv.DictReader(f))
    with db.atomic():
        for batch in chunked(rows, 100):
            User.insert_many([
                {"id": int(r["id"]), "username": r["username"], "email": r["email"], "created_at": parse_datetime(r["created_at"])}
                for r in batch
            ]).execute()


def load_urls(filepath="urls.csv"):
    with open(filepath) as f:
        rows = list(csv.DictReader(f))
    with db.atomic():
        for batch in chunked(rows, 100):
            Url.insert_many([
                {
                    "id": int(r["id"]),
                    "user": int(r["user_id"]),
                    "short_code": r["short_code"],
                    "original_url": r["original_url"],
                    "title": r["title"],
                    "is_active": r["is_active"] == "True",
                    "created_at": parse_datetime(r["created_at"]),
                    "updated_at": parse_datetime(r["updated_at"]),
                }
                for r in batch
            ]).execute()


def load_events(filepath="events.csv"):
    with open(filepath) as f:
        rows = list(csv.DictReader(f))
    with db.atomic():
        for batch in chunked(rows, 100):
            Event.insert_many([
                {
                    "id": int(r["id"]),
                    "url": int(r["url_id"]),
                    "user": int(r["user_id"]) if r["user_id"] else None,
                    "event_type": r["event_type"],
                    "timestamp": parse_datetime(r["timestamp"]),
                    "details": r["details"],
                }
                for r in batch
            ]).execute()


def load_all():
    db.create_tables([User, Url, Event])
    load_users()
    load_urls()
    load_events()
    # Reset sequences after bulk insert
    db.execute_sql("SELECT setval('user_id_seq', (SELECT MAX(id) FROM \"user\"))")
    db.execute_sql("SELECT setval('url_id_seq', (SELECT MAX(id) FROM url))")
    db.execute_sql("SELECT setval('event_id_seq', (SELECT MAX(id) FROM event))")
    print(f"Loaded {User.select().count()} users, {Url.select().count()} urls, {Event.select().count()} events")


if __name__ == "__main__":
    from app import create_app
    create_app()
    load_all()
