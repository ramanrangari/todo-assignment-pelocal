
# app.py
import sqlite3
from flask import Flask, jsonify, request, render_template, redirect, url_for
from datetime import datetime
import logging
import os

DB = os.environ.get("TODO_DB", "todo.db")

app = Flask(__name__, template_folder="templates")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("todo_app")

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    return dict(row) if row else None

@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks ORDER BY id DESC")
        rows = cur.fetchall()
        tasks = [dict_from_row(r) for r in rows]
        conn.close()
        return jsonify({"tasks": tasks}), 200
    except Exception as e:
        logger.exception("Failed to list tasks")
        return jsonify({"error": "internal_server_error", "message": str(e)}), 500

@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "not_found"}), 404
        return jsonify({"task": dict_from_row(row)}), 200
    except Exception as e:
        logger.exception("Failed to get task")
        return jsonify({"error": "internal_server_error", "message": str(e)}), 500

@app.route("/api/tasks", methods=["POST"])
def create_task():
    try:
        data = request.get_json(force=True)
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "validation_error", "message": "title is required"}), 400
        description = data.get("description")
        due_date = data.get("due_date")
        status = data.get("status") or "pending"
        if status not in ("pending", "in_progress", "done"):
            return jsonify({"error": "validation_error", "message": "invalid status"}), 400

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, description, due_date, status) VALUES (?, ?, ?, ?)",
            (title, description, due_date, status),
        )
        conn.commit()
        tid = cur.lastrowid
        cur.execute("SELECT * FROM tasks WHERE id = ?", (tid,))
        row = cur.fetchone()
        conn.close()
        return jsonify({"task": dict_from_row(row)}), 201
    except Exception as e:
        logger.exception("Failed to create task")
        return jsonify({"error": "internal_server_error", "message": str(e)}), 500

@app.route("/api/tasks/<int:task_id>", methods=["PATCH","PUT"])
def update_task(task_id):
    try:
        data = request.get_json(force=True)
        allowed = {"title","description","due_date","status"}
        updates = {k:v for k,v in data.items() if k in allowed}
        if "status" in updates and updates["status"] not in ("pending","in_progress","done"):
            return jsonify({"error":"validation_error","message":"invalid status"}), 400
        if not updates:
            return jsonify({"error":"validation_error","message":"no valid fields"}), 400

        set_clause = ", ".join([f"{k}=?" for k in updates]) + ", updated_at=CURRENT_TIMESTAMP"
        params = list(updates.values()) + [task_id]

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        if not cur.fetchone():
            conn.close()
            return jsonify({"error":"not_found"}),404

        cur.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", params)
        conn.commit()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        conn.close()
        return jsonify({"task": dict_from_row(row)}),200
    except Exception as e:
        logger.exception("Failed to update task")
        return jsonify({"error":"internal_server_error","message":str(e)}),500

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        if not cur.fetchone():
            conn.close()
            return jsonify({"error":"not_found"}),404
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return jsonify({"deleted":True}),200
    except Exception as e:
        logger.exception("Failed to delete task")
        return jsonify({"error":"internal_server_error","message":str(e)}),500

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/add", methods=["GET"])
def add_form():
    return render_template("form.html", action="Create", task=None)

@app.route("/edit/<int:task_id>", methods=["GET"])
def edit_form(task_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return "Task not found",404
        return render_template("form.html", action="Update", task=dict_from_row(row))
    except:
        return "Internal Server Error",500

@app.route("/health")
def health():
    return jsonify({"status":"ok"}),200

if __name__ == "__main__":
    if not os.path.exists(DB):
        from db_init import init_db
        init_db(DB)
    app.run(debug=True)
