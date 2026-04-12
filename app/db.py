import mysql.connector
from mysql.connector import pooling, Error
from flask import g, current_app


_pool = None


def init_pool(app):
    """Create a connection pool from Flask app config."""
    global _pool
    try:
        _pool = pooling.MySQLConnectionPool(
            pool_name="taskmatch_pool",
            pool_size=5,
            pool_reset_session=True,
            host=app.config["MYSQL_HOST"],
            port=app.config["MYSQL_PORT"],
            user=app.config["MYSQL_USER"],
            password=app.config["MYSQL_PASSWORD"],
            database=app.config["MYSQL_DB"],
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            autocommit=False,
        )
        print("[DB] Connection pool created successfully.")
    except Error as e:
        print(f"[DB] Pool creation failed: {e}")
        _pool = None


def get_db():
    """Return a connection from the pool, stored on Flask's g object."""
    if "db" not in g:
        if _pool is None:
            raise RuntimeError("Database pool not initialised. Check your .env settings.")
        g.db = _pool.get_connection()
    return g.db


def close_db(e=None):
    """Return the connection to the pool at end of request."""
    db = g.pop("db", None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass


def query(sql, params=None, one=False, commit=False):
    """
    Execute a SQL query and return results as list of dicts (SELECT)
    or lastrowid (INSERT/UPDATE/DELETE when commit=True).
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        if commit:
            conn.commit()
            return cursor.lastrowid
        rows = cursor.fetchall()
        return rows[0] if one and rows else (None if one else rows)
    except Error as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        cursor.close()


def execute(sql, params=None):
    """Shortcut for INSERT / UPDATE / DELETE (auto-commits)."""
    return query(sql, params, commit=True)
