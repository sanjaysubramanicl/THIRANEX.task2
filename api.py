"""
JSON REST API for tasks. All endpoints require a logged-in session
(handled by Flask-Login) so each user only ever sees their own tasks.
"""
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from models import db, Task

api_bp = Blueprint("api", __name__)


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


@api_bp.route("/tasks", methods=["GET"])
@login_required
def list_tasks():
    status = request.args.get("status")
    query = Task.query.filter_by(user_id=current_user.id)
    if status:
        query = query.filter_by(status=status)
    tasks = query.order_by(Task.due_date.is_(None), Task.due_date.asc()).all()
    return jsonify([t.to_dict() for t in tasks])


@api_bp.route("/tasks/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())


@api_bp.route("/tasks", methods=["POST"])
@login_required
def create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400

    try:
        due_date = _parse_date(data.get("due_date"))
    except ValueError:
        return jsonify({"error": "due_date must be YYYY-MM-DD"}), 400

    task = Task(
        title=title,
        description=data.get("description", ""),
        status=data.get("status", "todo"),
        priority=data.get("priority", "medium"),
        due_date=due_date,
        user_id=current_user.id,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@api_bp.route("/tasks/<int:task_id>", methods=["PUT", "PATCH"])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "Title cannot be empty"}), 400
        task.title = title
    if "description" in data:
        task.description = data.get("description", "")
    if "status" in data:
        task.status = data.get("status")
    if "priority" in data:
        task.priority = data.get("priority")
    if "due_date" in data:
        try:
            task.due_date = _parse_date(data.get("due_date"))
        except ValueError:
            return jsonify({"error": "due_date must be YYYY-MM-DD"}), 400

    db.session.commit()
    return jsonify(task.to_dict())


@api_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"result": "deleted", "id": task_id})
