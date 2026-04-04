import csv
import io
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict

from app.database import db
from app.models.user import User

users_bp = Blueprint("users", __name__)


@users_bp.route("/users")
def list_users():
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(100, max(1, request.args.get("per_page", 20, type=int)))
    users = User.select().order_by(User.id).paginate(page, per_page)
    return jsonify([model_to_dict(u) for u in users])


@users_bp.route("/users/<int:user_id>")
def get_user(user_id):
    user = User.get_or_none(User.id == user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(model_to_dict(user))


@users_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)
    if not data or "username" not in data or "email" not in data:
        return jsonify({"error": "username and email are required"}), 400
    if not isinstance(data["username"], str) or not isinstance(data["email"], str):
        return jsonify({"error": "username and email must be strings"}), 400
    if User.get_or_none(User.username == data["username"]):
        return jsonify({"error": "Username already exists"}), 400
    if User.get_or_none(User.email == data["email"]):
        return jsonify({"error": "Email already exists"}), 400

    user = User.create(
        username=data["username"],
        email=data["email"],
        created_at=datetime.now(timezone.utc),
    )
    return jsonify(model_to_dict(user)), 201


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.get_or_none(User.id == user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if "username" in data:
        if not isinstance(data["username"], str):
            return jsonify({"error": "username must be a string"}), 400
        user.username = data["username"]
    if "email" in data:
        if not isinstance(data["email"], str):
            return jsonify({"error": "email must be a string"}), 400
        user.email = data["email"]
    user.save()
    return jsonify(model_to_dict(user))


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.get_or_none(User.id == user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.delete_instance(recursive=True)
    return jsonify({"message": "User deleted"}), 200


@users_bp.route("/users/bulk", methods=["POST"])
def bulk_load_users():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    stream = io.StringIO(file.stream.read().decode("utf-8"))
    reader = csv.DictReader(stream)
    count = 0
    with db.atomic():
        for row in reader:
            User.get_or_create(
                username=row["username"],
                defaults={
                    "email": row["email"],
                    "created_at": row.get("created_at", datetime.now(timezone.utc)),
                },
            )
            count += 1
    return jsonify({"imported": count}), 201
