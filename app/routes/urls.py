import json
import random
import string
from datetime import datetime

from flask import Blueprint, abort, jsonify, redirect, request
from playhouse.shortcuts import model_to_dict

from app.models import Event, Url, User

urls_bp = Blueprint("urls", __name__)


def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if not Url.select().where(Url.short_code == code).exists():
            return code


@urls_bp.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()
    if not data or not data.get("url"):
        return jsonify(error="url is required"), 400

    user_id = data.get("user_id")
    if not user_id:
        return jsonify(error="user_id is required"), 400

    user = User.get_or_none(User.id == user_id)
    if not user:
        return jsonify(error="user not found"), 404

    now = datetime.now()
    url = Url.create(
        user=user,
        short_code=generate_short_code(),
        original_url=data["url"],
        title=data.get("title"),
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    Event.create(
        url=url,
        user=user,
        event_type="created",
        timestamp=now,
        details=json.dumps({"short_code": url.short_code, "original_url": url.original_url}),
    )

    return jsonify(short_code=url.short_code, short_url=f"/{url.short_code}"), 201


@urls_bp.route("/<short_code>")
def redirect_url(short_code):
    url = Url.get_or_none(Url.short_code == short_code)
    if not url or not url.is_active:
        abort(404)

    Event.create(
        url=url,
        user=None,
        event_type="click",
        timestamp=datetime.now(),
        details=json.dumps({"referrer": request.referrer, "user_agent": request.user_agent.string}),
    )

    return redirect(url.original_url, code=302)


@urls_bp.route("/urls/<short_code>")
def get_url(short_code):
    url = Url.get_or_none(Url.short_code == short_code)
    if not url:
        abort(404)
    return jsonify(model_to_dict(url, backrefs=False))


@urls_bp.route("/urls/<short_code>/stats")
def get_stats(short_code):
    url = Url.get_or_none(Url.short_code == short_code)
    if not url:
        abort(404)
    clicks = Event.select().where(Event.url == url, Event.event_type == "click").count()
    return jsonify(short_code=url.short_code, clicks=clicks, is_active=url.is_active)
