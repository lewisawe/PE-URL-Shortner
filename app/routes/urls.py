import json
import random
import string
from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import Blueprint, jsonify, redirect, request
from peewee import IntegrityError
from playhouse.shortcuts import model_to_dict

from app.database import db
from app.models.event import Event
from app.models.url import Url
from app.models.user import User

urls_bp = Blueprint("urls", __name__)


def generate_short_code():
    return "".join(random.choices(string.ascii_letters + string.digits, k=6))


def is_valid_url(url):
    try:
        r = urlparse(url)
        return all([r.scheme in ("http", "https"), r.netloc])
    except Exception:
        return False


def serialize_url(url):
    d = model_to_dict(url, backrefs=False)
    if "user" in d and isinstance(d["user"], dict):
        d["user_id"] = d["user"]["id"]
        del d["user"]
    elif "user" in d:
        d["user_id"] = d["user"]
        del d["user"]
    return d


@urls_bp.route("/urls")
def list_urls():
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(100, max(1, request.args.get("per_page", 20, type=int)))
    user_id = request.args.get("user_id", type=int)
    is_active = request.args.get("is_active")

    query = Url.select().order_by(Url.id)
    if user_id:
        query = query.where(Url.user == user_id)
    if is_active is not None:
        query = query.where(Url.is_active == (is_active.lower() == "true"))
    return jsonify([serialize_url(u) for u in query.paginate(page, per_page)])


@urls_bp.route("/urls/<int:url_id>")
def get_url(url_id):
    url = Url.get_or_none(Url.id == url_id)
    if not url:
        return jsonify({"error": "URL not found"}), 404
    return jsonify(serialize_url(url))


@urls_bp.route("/urls", methods=["POST"])
def create_url():
    data = request.get_json(silent=True)
    if not data or "original_url" not in data or "user_id" not in data:
        return jsonify({"error": "original_url and user_id are required"}), 400
    if not is_valid_url(data["original_url"]):
        return jsonify({"error": "Invalid URL format"}), 400

    user = User.get_or_none(User.id == data["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    now = datetime.now(timezone.utc)
    for _ in range(5):
        try:
            with db.atomic():
                url = Url.create(
                    user=user, short_code=generate_short_code(),
                    original_url=data["original_url"], title=data.get("title"),
                    is_active=True, created_at=now, updated_at=now,
                )
                Event.create(
                    url=url, user=user, event_type="created", timestamp=now,
                    details=json.dumps({"short_code": url.short_code, "original_url": data["original_url"]}),
                )
            return jsonify(serialize_url(url)), 201
        except IntegrityError:
            continue
    return jsonify({"error": "Failed to generate unique short code"}), 500


@urls_bp.route("/urls/<int:url_id>", methods=["PUT"])
def update_url(url_id):
    url = Url.get_or_none(Url.id == url_id)
    if not url:
        return jsonify({"error": "URL not found"}), 404
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if "original_url" in data and not is_valid_url(data["original_url"]):
        return jsonify({"error": "Invalid URL format"}), 400

    now = datetime.now(timezone.utc)
    if "title" in data:
        url.title = data["title"]
    if "original_url" in data:
        url.original_url = data["original_url"]
    if "is_active" in data:
        url.is_active = data["is_active"]
    url.updated_at = now

    with db.atomic():
        url.save()
        Event.create(url=url, user=url.user, event_type="updated", timestamp=now)
    return jsonify(serialize_url(url))


@urls_bp.route("/urls/<int:url_id>", methods=["DELETE"])
def delete_url(url_id):
    url = Url.get_or_none(Url.id == url_id)
    if not url:
        return jsonify({"error": "URL not found"}), 404
    with db.atomic():
        url.delete_instance(recursive=True)
    return jsonify({"message": "URL deleted"}), 200


@urls_bp.route("/<short_code>")
def redirect_short(short_code):
    url = Url.get_or_none(Url.short_code == short_code)
    if not url:
        return jsonify({"error": "Short code not found"}), 404
    if not url.is_active:
        return jsonify({"error": "URL is inactive"}), 410
    return redirect(url.original_url)
