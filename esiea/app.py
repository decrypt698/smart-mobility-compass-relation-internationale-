from flask import Flask, render_template, request, redirect, url_for,send_file
from werkzeug.utils import secure_filename
import tempfile
import sqlite3
import os
import requests
import time
from io import BytesIO
from PyPDF2 import PdfMerger
from five_years_filter import generer_top_commentaires
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


def get_sections(page_name):
    conn = get_db_connection()
    sections = conn.execute("""
        SELECT * FROM sections
        WHERE page_name = ? AND is_deleted = 0
        ORDER BY section_order ASC
    """, (page_name,)).fetchall()
    conn.close()
    return sections


def get_next_order(page_name):
    conn = get_db_connection()
    row = conn.execute("""
        SELECT MAX(section_order) AS max_order
        FROM sections
        WHERE page_name = ?
    """, (page_name,)).fetchone()
    conn.close()
    return (row["max_order"] or 0) + 1


def insert_section(page_name, form):
    title = form.get("title", "").strip()
    caption = form.get("caption", "").strip()
    description = form.get("description", "").strip()
    powerbi_link = form.get("powerbi_link", "").strip()
    pdf_file = form.get("pdf_file", "").strip()
    workspace_id = form.get("workspace_id", "").strip()
    report_id = form.get("report_id", "").strip()

    new_order = get_next_order(page_name)

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO sections (
            page_name, section_order, section_label, title, caption,
            description, powerbi_link, pdf_file, is_deleted,
            workspace_id, report_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
    """, (
        page_name,
        new_order,
        f"Section {new_order}",
        title,
        caption,
        description,
        powerbi_link,
        pdf_file,
        workspace_id,
        report_id
    ))
    conn.commit()
    conn.close()


def update_section(page_name, section_id, form):
    title = form.get("title", "").strip()
    caption = form.get("caption", "").strip()
    description = form.get("description", "").strip()
    powerbi_link = form.get("powerbi_link", "").strip()
    pdf_file = form.get("pdf_file", "").strip()
    workspace_id = form.get("workspace_id", "").strip()
    report_id = form.get("report_id", "").strip()

    conn = get_db_connection()
    conn.execute("""
        UPDATE sections
        SET title = ?, caption = ?, description = ?, powerbi_link = ?, pdf_file = ?,
            workspace_id = ?, report_id = ?
        WHERE id = ? AND page_name = ?
    """, (
        title, caption, description, powerbi_link, pdf_file,
        workspace_id, report_id, section_id, page_name
    ))
    conn.commit()
    conn.close()


def soft_delete_section(page_name, section_id):
    conn = get_db_connection()
    conn.execute("""
        UPDATE sections
        SET is_deleted = 1
        WHERE id = ? AND page_name = ?
    """, (section_id, page_name))
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return redirect(url_for("dashboard_ri"))

@app.route("/traiter-excel-commentaires", methods=["GET", "POST"])
def traiter_excel_commentaires():
    if request.method == "GET":
        return "", 204

    if "excel_file" not in request.files:
        return "Aucun fichier envoyé."

    fichier = request.files["excel_file"]

    if fichier.filename == "":
        return "Aucun fichier sélectionné."

    nom_fichier = secure_filename(fichier.filename)

    with tempfile.TemporaryDirectory() as temp_dir:
        chemin_entree = os.path.join(temp_dir, nom_fichier)
        chemin_sortie = os.path.join(temp_dir, "top10_commentaires_par_institution_test_(5 années).xlsx")

        fichier.save(chemin_entree)

        try:
            generer_top_commentaires(
                fichier_entree=chemin_entree,
                fichier_sortie=chemin_sortie
            )
        except Exception as e:
            return f"Erreur pendant le traitement : {str(e)}"

        with open(chemin_sortie, "rb") as f:
            output = BytesIO(f.read())

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="top10_commentaires_par_institution_test_(5 années).xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
# =========================
# DASHBOARD RI
# =========================
@app.route("/dashboard-ri")
def dashboard_ri():
    sections = get_sections("dashboard_ri")
    return render_template("dashboard_ri.html", sections=sections)


@app.route("/add-section", methods=["POST"])
def add_section():
    insert_section("dashboard_ri", request.form)
    return redirect(url_for("dashboard_ri"))


@app.route("/edit-section/<int:section_id>", methods=["POST"])
def edit_section(section_id):
    update_section("dashboard_ri", section_id, request.form)
    return redirect(url_for("dashboard_ri"))


@app.route("/delete-section/<int:section_id>", methods=["POST"])
def delete_section(section_id):
    soft_delete_section("dashboard_ri", section_id)
    return redirect(url_for("dashboard_ri"))


# =========================
# SATISFACTION RI
# =========================
@app.route("/satisfaction-ri")
def satisfaction_ri():
    sections = get_sections("satisfaction_ri")
    return render_template("satisfaction_ri.html", sections=sections)


@app.route("/add-satisfaction-section", methods=["POST"])
def add_satisfaction_section():
    insert_section("satisfaction_ri", request.form)
    return redirect(url_for("satisfaction_ri"))


@app.route("/edit-satisfaction-section/<int:section_id>", methods=["POST"])
def edit_satisfaction_section(section_id):
    update_section("satisfaction_ri", section_id, request.form)
    return redirect(url_for("satisfaction_ri"))


@app.route("/delete-satisfaction-section/<int:section_id>", methods=["POST"])
def delete_satisfaction_section(section_id):
    soft_delete_section("satisfaction_ri", section_id)
    return redirect(url_for("satisfaction_ri"))


# =========================
# BUDGET RI
# =========================
@app.route("/budget-ri")
def budget_ri():
    sections = get_sections("budget_ri")
    return render_template("budget_ri.html", sections=sections)


@app.route("/add-budget-section", methods=["POST"])
def add_budget_section():
    insert_section("budget_ri", request.form)
    return redirect(url_for("budget_ri"))


@app.route("/edit-budget-section/<int:section_id>", methods=["POST"])
def edit_budget_section(section_id):
    update_section("budget_ri", section_id, request.form)
    return redirect(url_for("budget_ri"))


@app.route("/delete-budget-section/<int:section_id>", methods=["POST"])
def delete_budget_section(section_id):
    soft_delete_section("budget_ri", section_id)
    return redirect(url_for("budget_ri"))


# =========================
# AMELIORATION RI
# =========================
@app.route("/amelioration-ri")
def amelioration_ri():
    sections = get_sections("amelioration_ri")
    return render_template("amelioration_ri.html", sections=sections)


@app.route("/add-amelioration-section", methods=["POST"])
def add_amelioration_section():
    insert_section("amelioration_ri", request.form)
    return redirect(url_for("amelioration_ri"))


@app.route("/edit-amelioration-section/<int:section_id>", methods=["POST"])
def edit_amelioration_section(section_id):
    update_section("amelioration_ri", section_id, request.form)
    return redirect(url_for("amelioration_ri"))


@app.route("/delete-amelioration-section/<int:section_id>", methods=["POST"])
def delete_amelioration_section(section_id):
    soft_delete_section("amelioration_ri", section_id)
    return redirect(url_for("amelioration_ri"))

@app.route("/download-all-reports")
def download_all_reports():
    pass

if __name__ == "__main__":
    print("BASE_DIR :", BASE_DIR)
    print("dashboard_ri.html trouvé :", os.path.exists(os.path.join(BASE_DIR, "dashboard_ri.html")))
    print("satisfaction_ri.html trouvé :", os.path.exists(os.path.join(BASE_DIR, "satisfaction_ri.html")))
    print("budget_ri.html trouvé :", os.path.exists(os.path.join(BASE_DIR, "budget_ri.html")))
    print("amelioration_ri.html trouvé :", os.path.exists(os.path.join(BASE_DIR, "amelioration_ri.html")))
    print("database.db trouvé :", os.path.exists(os.path.join(BASE_DIR, "database.db")))
    app.run(debug=True)