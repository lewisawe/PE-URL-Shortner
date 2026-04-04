import json
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict

from app.models.event import Event
from app.models.url import Url
from app.models.user import User

events_bp = Blueprint("events", __name__)


def serialize_event(event):
    d = model_to_dict(event, backrefs=False)
    if "url" in d and isinstance(d["url"], dict):
        d["url_id"] = d["url"]["id"]
        del d["url"]
    elif "url" in d:
        d["url_id"] = d["url"]
        del d["url"]
    if "user" in d and isinstance(d["user"], dict):
        d["user_id"] = d["user"]["id"]
        del d["user"]
    elif "user" in d:
        d["user_id"] = d["user"]
        del d["user"]
    if isinstance(d.get("details"), str):
        try:
            d["details"] = json.loads(d["details"])
        except (json.JSONDecodeError, TypeError):
            pass
    return d


@events_bp.route("/events")
def list_events():
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(100, max(1, request.args.get("per_page", 20, type=int)))
    url_id = request.args.get("url_id", type=int)
    user_id = request.args.get("user_id", type=int)
    event_type = request.args.get("event_type")

    query = Event.select().order_by(Event.id)
    if url_id:
        query = query.where(Event.url == url_id)
    if user_id:
        query = query.where(Event.user == user_id)
    if event_type:
        query = query.where(Event.event_type == event_type)
    return jsonify([serialize_event(e) for e in query.paginate(page, per_page)])


@events_bp.route("/events/<int:event_id>")
def get_event(event_id):
    event = Event.get_or_none(Event.id == event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(serialize_event(event))


@events_bp.route("/events", methods=["POST"])
def create_event():
    data = request.get_json(silent=True)
    if not data or "event_type" not in data or "url_id" not in data:
        return jsonify({"error": "event_type and url_id are required"}), 400
    if not isinstance(data["event_type"], str) or not data["event_type"].strip():
        return jsonify({"error": "event_type must be a non-empty string"}), 400
    if not isinstance(data["url_id"], int):
        return jsonify({"error": "url_id must be an integer"}), 400
    if data.get("user_id") is not None and not isinstance(data["user_id"], int):
        return jsonify({"error": "user_id must be an integer"}), 400

    url = Url.get_or_none(Url.id == data["url_id"])
    if not url:
        return jsonify({"error": "URL not found"}), 404

    user = None
    if data.get("user_id") is not None:
        user = User.get_or_none(User.id == data["user_id"])
        if not user:
            return jsonify({"error": "User not found"}), 404

    details = data.get("details")
    # Fractured Vessel + Deceitful Scroll: details must be a dict or None, not a plain string
    if details is not None and not isinstance(details, dict):
        return jsonify({"error": "details must be a JSON object"}), 400
    if isinstance(details, dict):
        details = json.dumps(details)

    event = Event.create(
        url=url, user=user, event_type=data["event_type"],
        timestamp=datetime.now(timezone.utc), details=details,
    )
    return jsonify(serialize_event(event)), 201
