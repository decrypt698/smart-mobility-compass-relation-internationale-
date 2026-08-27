from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import requests
import time
from io import BytesIO
from flask import send_file
from PyPDF2 import PdfMerger
import msal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=BASE_DIR,
    static_folder=BASE_DIR,
    static_url_path=""
)

def get_db_connection():
    db_path = os.path.join(BASE_DIR, "database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return redirect(url_for("dashboard_ri"))


# =========================
# DASHBOARD RI
# =========================
@app.route("/dashboard-ri")
def dashboard_ri():
    conn = get_db_connection()
    sections = conn.execute("""
        SELECT * FROM sections
        WHERE page_name = 'dashboard_ri' AND is_deleted = 0
        ORDER BY section_order ASC
    """).fetchall()
    conn.close()
    return render_template("dashboard_ri.html", sections=sections)


@app.route("/add-section", methods=["POST"])
def add_section():
    title = request.form.get("title", "").strip()
    caption = request.form.get("caption", "").strip()
    description = request.form.get("description", "").strip()
    powerbi_link = request.form.get("powerbi_link", "").strip()
    pdf_file = request.form.get("pdf_file", "").strip()

    conn = get_db_connection()

    last_order_row = conn.execute("""
        SELECT MAX(section_order) AS max_order
        FROM sections
        WHERE page_name = 'dashboard_ri'
    """).fetchone()

    last_order = last_order_row["max_order"] if last_order_row["max_order"] is not None else 0
    new_order = last_order + 1

    conn.execute("""
        INSERT INTO sections (
            page_name, section_order, section_label, title, caption,
            description, powerbi_link, pdf_file, is_deleted
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        "dashboard_ri",
        new_order,
        f"Section {new_order}",
        title,
        caption,
        description,
        powerbi_link,
        pdf_file
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard_ri"))


@app.route("/edit-section/<int:section_id>", methods=["POST"])
def edit_section(section_id):
    title = request.form.get("title", "").strip()
    caption = request.form.get("caption", "").strip()
    description = request.form.get("description", "").strip()
    powerbi_link = request.form.get("powerbi_link", "").strip()
    pdf_file = request.form.get("pdf_file", "").strip()

    conn = get_db_connection()
    conn.execute("""
        UPDATE sections
        SET title = ?, caption = ?, description = ?, powerbi_link = ?, pdf_file = ?
        WHERE id = ? AND page_name = 'dashboard_ri'
    """, (title, caption, description, powerbi_link, pdf_file, section_id))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard_ri"))


@app.route("/delete-section/<int:section_id>", methods=["POST"])
def delete_section(section_id):
    conn = get_db_connection()
    conn.execute("""
        UPDATE sections
        SET is_deleted = 1
        WHERE id = ? AND page_name = 'dashboard_ri'
    """, (section_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard_ri"))


# =========================
# SATISFACTION RI
# =========================
@app.route("/satisfaction-ri")
def satisfaction_ri():
    conn = get_db_connection()
    sections = conn.execute("""
        SELECT * FROM sections
        WHERE page_name = 'satisfaction_ri' AND is_deleted = 0
        ORDER BY section_order ASC
    """).fetchall()
    conn.close()
    return render_template("satisfaction_ri.html", sections=sections)


@app.route("/add-satisfaction-section", methods=["POST"])
def add_satisfaction_section():
    title = request.form.get("title", "").strip()
    caption = request.form.get("caption", "").strip()
    description = request.form.get("description", "").strip()
    powerbi_link = request.form.get("powerbi_link", "").strip()
    pdf_file = request.form.get("pdf_file", "").strip()

    conn = get_db_connection()

    last_order_row = conn.execute("""
        SELECT MAX(section_order) AS max_order
        FROM sections
        WHERE page_name = 'satisfaction_ri'
    """).fetchone()

    last_order = last_order_row["max_order"] if last_order_row["max_order"] is not None else 0
    new_order = last_order + 1

    conn.execute("""
        INSERT INTO sections (
            page_name, section_order, section_label, title, caption,
            description, powerbi_link, pdf_file, is_deleted
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        "satisfaction_ri",
        new_order,
        f"Section {new_order}",
        title,
        caption,
        description,
        powerbi_link,
        pdf_file
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("satisfaction_ri"))


@app.route("/edit-satisfaction-section/<int:section_id>", methods=["POST"])
def edit_satisfaction_section(section_id):
    title = request.form.get("title", "").strip()
    caption = request.form.get("caption", "").strip()
    description = request.form.get("description", "").strip()
    powerbi_link = request.form.get("powerbi_link", "").strip()
    pdf_file = request.form.get("pdf_file", "").strip()

    conn = get_db_connection()
    conn.execute("""
        UPDATE sections
        SET title = ?, caption = ?, description = ?, powerbi_link = ?, pdf_file = ?
        WHERE id = ? AND page_name = 'satisfaction_ri'
    """, (title, caption, description, powerbi_link, pdf_file, section_id))
    conn.commit()
    conn.close()

    return redirect(url_for("satisfaction_ri"))


@app.route("/delete-satisfaction-section/<int:section_id>", methods=["POST"])
def delete_satisfaction_section(section_id):
    conn = get_db_connection()
    conn.execute("""
        UPDATE sections
        SET is_deleted = 1
        WHERE id = ? AND page_name = 'satisfaction_ri'
    """, (section_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("satisfaction_ri"))


# =========================
# BUDGET RI
# =========================
@app.route("/budget-ri")
def budget_ri():
    conn = get_db_connection()
    sections = conn.execute("""
        SELECT * FROM sections
        WHERE page_name = 'budget_ri' AND is_deleted = 0
        ORDER BY section_order ASC
    """).fetchall()
    conn.close()
    return render_template("budget_ri.html", sections=sections)


@app.route("/add-budget-section", methods=["POST"])
def add_budget_section():
    title = request.form.get("title", "").strip()
    caption = request.form.get("caption", "").strip()
    description = request.form.get("description", "").strip()
    powerbi_link = request.form.get("powerbi_link", "").strip()
    pdf_file = request.form.get("pdf_file", "").strip()

    conn = get_db_connection()

    last_order_row = conn.execute("""
        SELECT MAX(section_order) AS max_order
        FROM sections
        WHERE page_name = 'budget_ri'
    """).fetchone()

    last_order = last_order_row["max_order"] if last_order_row["max_order"] is not None else 0
    new_order = last_order + 1

    conn.execute("""
        INSERT INTO sections (
            page_name, section_order, section_label, title, caption,
            description, powerbi_link, pdf_file, is_deleted
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        "budget_ri",
        new_order,
        f"Section {new_order}",
        title,
        caption,
        description,
        powerbi_link,
        pdf_file
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("budget_ri"))


@app.route("/edit-budget-section/<int:section_id>", methods=["POST"])
def edit_budget_section(section_id):
    title = request.form.get("title", "").strip()
    caption = request.form.get("caption", "").strip()
    description = request.form.get("description", "").strip()
    powerbi_link = request.form.get("powerbi_link", "").strip()
    pdf_file = request.form.get("pdf_file", "").strip()

    conn = get_db_connection()
    conn.execute("""
        UPDATE sections
        SET title = ?, caption = ?, description = ?, powerbi_link = ?, pdf_file = ?
        WHERE id = ? AND page_name = 'budget_ri'
    """, (title, caption, description, powerbi_link, pdf_file, section_id))
    conn.commit()
    conn.close()

    return redirect(url_for("budget_ri"))


@app.route("/delete-budget-section/<int:section_id>", methods=["POST"])
def delete_budget_section(section_id):
    conn = get_db_connection()
    conn.execute("""
        UPDATE sections
        SET is_deleted = 1
        WHERE id = ? AND page_name = 'budget_ri'
    """, (section_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("budget_ri"))
# =========================
# AMELIORATION RI
# =========================
@app.route("/amelioration-ri")
def amelioration_ri():
    conn = get_db_connection()
    sections = conn.execute("""
        SELECT * FROM sections
        WHERE page_name = 'amelioration_ri' AND is_deleted = 0
        ORDER BY section_order ASC
    """).fetchall()
    conn.close()
    return render_template("amelioration_ri.html", sections=sections)


@app.route("/add-amelioration-section", methods=["POST"])
def add_amelioration_section():
    title = request.form.get("title", "").strip()
    caption = request.form.get("caption", "").strip()
    description = request.form.get("description", "").strip()
    powerbi_link = request.form.get("powerbi_link", "").strip()
    pdf_file = request.form.get("pdf_file", "").strip()

    conn = get_db_connection()

    last_order_row = conn.execute("""
        SELECT MAX(section_order) AS max_order
        FROM sections
        WHERE page_name = 'budget_ri'
    """).fetchone()

    last_order = last_order_row["max_order"] if last_order_row["max_order"] is not None else 0
    new_order = last_order + 1

    conn.execute("""
        INSERT INTO sections (
            page_name, section_order, section_label, title, caption,
            description, powerbi_link, pdf_file, is_deleted
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        "amelioration_ri",
        new_order,
        f"Section {new_order}",
        title,
        caption,
        description,
        powerbi_link,
        pdf_file
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("amelioration_ri"))


@app.route("/edit-amelioration-section/<int:section_id>", methods=["POST"])
def edit_amelioration_section(section_id):
    title = request.form.get("title", "").strip()
    caption = request.form.get("caption", "").strip()
    description = request.form.get("description", "").strip()
    powerbi_link = request.form.get("powerbi_link", "").strip()
    pdf_file = request.form.get("pdf_file", "").strip()

    conn = get_db_connection()
    conn.execute("""
        UPDATE sections
        SET title = ?, caption = ?, description = ?, powerbi_link = ?, pdf_file = ?
        WHERE id = ? AND page_name = 'amelioration_ri'
    """, (title, caption, description, powerbi_link, pdf_file, section_id))
    conn.commit()
    conn.close()

    return redirect(url_for("amelioration_ri"))


@app.route("/delete-amelioration-section/<int:section_id>", methods=["POST"])
def delete_amelioration_section(section_id):
    conn = get_db_connection()
    conn.execute("""
        UPDATE sections
        SET is_deleted = 1
        WHERE id = ? AND page_name = 'amelioration_ri'
    """, (section_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("amelioration_ri"))



if __name__ == "__main__":
    print("BASE_DIR :", BASE_DIR)
    print("dashboard_ri.html trouvé :", os.path.exists(os.path.join(BASE_DIR, "dashboard_ri.html")))
    print("satisfaction_ri.html trouvé :", os.path.exists(os.path.join(BASE_DIR, "satisfaction_ri.html")))
    print("budget_ri.html trouvé :", os.path.exists(os.path.join(BASE_DIR, "budget_ri.html")))
    print("amelioration_ri.html trouvé :", os.path.exists(os.path.join(BASE_DIR, "amelioration_ri.html")))
    print("database.db trouvé :", os.path.exists(os.path.join(BASE_DIR, "database.db")))
    app.run(debug=True)