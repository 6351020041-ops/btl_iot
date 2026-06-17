from flask import Flask, render_template, request, jsonify, Response, send_file
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB = "database.db"


# ================= LOGO =================

@app.route("/logo.png")
def logo():
    return send_file("logo.png")


# ================= DATABASE =================

def db():
    conn = sqlite3.connect(
        DB,
        timeout=30,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def today():
    return datetime.now().strftime("%Y-%m-%d")


def now():
    return datetime.now().strftime("%H:%M:%S")


# ================= INIT DATABASE =================

def init():

    conn = db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS students(
        uid TEXT PRIMARY KEY,
        mssv TEXT,
        name TEXT,
        class TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        uid TEXT,
        mssv TEXT,
        name TEXT,
        class TEXT,
        date TEXT,
        check_in TEXT,
        check_out TEXT
    )
    """)

    conn.commit()
    conn.close()

init()


# ================= HOME =================

@app.route("/")
def home():
    return render_template("webtest.html")


# ================= ADD STUDENT =================

@app.route("/add-student", methods=["POST"])
def add_student():

    data = request.json

    conn = db()

    conn.execute("""
    INSERT OR REPLACE INTO students(
        uid,
        mssv,
        name,
        class
    )
    VALUES(?,?,?,?)
    """, (
        data["uid"],
        data["mssv"],
        data["name"],
        data["class"]
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "ok"
    })


# ================= RFID SCAN =================

@app.route("/scan", methods=["POST"])
def scan():

    uid = request.json["uid"]

    conn = db()

    student = conn.execute("""
    SELECT *
    FROM students
    WHERE uid=?
    """, (uid,)).fetchone()

    if not student:

        conn.close()

        return jsonify({
            "status": "error",
            "msg": "THẺ CHƯA ĐĂNG KÝ"
        })

    mssv = student["mssv"]
    name = student["name"]
    class_name = student["class"]

    log = conn.execute("""
    SELECT *
    FROM logs
    WHERE uid=? AND date=?
    """, (
        uid,
        today()
    )).fetchone()

    # CHECK IN
    if log is None:

        conn.execute("""
        INSERT INTO logs(
            uid,
            mssv,
            name,
            class,
            date,
            check_in,
            check_out
        )
        VALUES(?,?,?,?,?,?,?)
        """, (
            uid,
            mssv,
            name,
            class_name,
            today(),
            now(),
            ""
        ))

        msg = "CHECK IN"

    # CHECK OUT
    elif log["check_out"] == "":

        conn.execute("""
        UPDATE logs
        SET check_out=?
        WHERE uid=? AND date=?
        """, (
            now(),
            uid,
            today()
        ))

        msg = "CHECK OUT"

    else:

        conn.close()

        return jsonify({
            "status": "done",
            "msg": "ĐÃ ĐIỂM DANH",
            "name": name,
            "mssv": mssv,
            "class": class_name
        })

    conn.commit()
    conn.close()

    return jsonify({
        "status": "ok",
        "msg": msg,
        "name": name,
        "mssv": mssv,
        "class": class_name
    })


# ================= GET LOGS =================

@app.route("/logs")
def logs():

    conn = db()

    data = conn.execute("""
    SELECT *
    FROM logs
    WHERE date=?
    ORDER BY rowid DESC
    LIMIT 50
    """, (today(),)).fetchall()

    conn.close()

    return jsonify([
        dict(i) for i in data
    ])


# ================= DELETE LOG =================

@app.route("/delete-log", methods=["POST"])
def delete_log():

    data = request.json

    conn = db()

    conn.execute("""
    DELETE FROM logs
    WHERE uid=? AND date=?
    """, (
        data["uid"],
        data["date"]
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "ok",
        "msg": "Đã xóa điểm danh"
    })


# ================= DELETE STUDENT =================

@app.route("/delete-student", methods=["POST"])
def delete_student():

    uid = request.json["uid"]

    conn = db()

    conn.execute("""
    DELETE FROM students
    WHERE uid=?
    """, (uid,))

    conn.execute("""
    DELETE FROM logs
    WHERE uid=?
    """, (uid,))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "ok",
        "msg": "Đã xóa sinh viên"
    })


# ================= EXPORT CSV =================

@app.route("/export")
def export():

    conn = db()

    data = conn.execute("""
    SELECT *
    FROM logs
    WHERE date=?
    """, (today(),)).fetchall()

    conn.close()

    def generate():

        yield "UID,MSSV,Name,Class,Date,CheckIn,CheckOut\n"

        for i in data:

            yield (
                f"{i['uid']},"
                f"{i['mssv']},"
                f"{i['name']},"
                f"{i['class']},"
                f"{i['date']},"
                f"{i['check_in']},"
                f"{i['check_out']}\n"
            )

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename=Attendance_{today()}.csv"
        }
    )


# ================= RUN =================
from waitress import serve

if __name__ == "__main__":
    serve(
        app,
        host="0.0.0.0",
        port=5000,
        threads=8
    )