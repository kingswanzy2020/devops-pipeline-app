import os
import time
from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Database connection settings from environment variables
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "appdb")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "postgres")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


def init_db():
    """Create tables if they do not exist. Retries on connection failure."""
    retries = 5
    for i in range(retries):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("Database initialized successfully.")
            return
        except Exception as e:
            print(f"DB connection attempt {i+1}/{retries} failed: {e}")
            time.sleep(3)
    print("WARNING: Could not initialize database after retries.")


@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": str(e)}), 500


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, description, created_at FROM tasks ORDER BY created_at DESC;")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {"id": t[0], "title": t[1], "description": t[2],
            "created_at": str(t[3])}
        for t in tasks
    ])


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    title = data.get("title", "")
    description = data.get("description", "")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s) RETURNING id;",
        (title, description)
    )
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": task_id, "title": title, "description": description}), 201


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Task deleted"}), 200


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
