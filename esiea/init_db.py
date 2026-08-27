import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# =========================
# CREATION TABLE
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_name TEXT NOT NULL,
    section_order INTEGER NOT NULL,
    section_label TEXT,
    title TEXT NOT NULL,
    caption TEXT,
    description TEXT,
    powerbi_link TEXT,
    pdf_file TEXT,
    is_deleted INTEGER DEFAULT 0,
    workspace_id TEXT,
    report_id TEXT
)
""")

# =========================
# RESET DATA
# =========================
cursor.execute("DELETE FROM sections")

# =========================
# DATA
# =========================
sections_data = [

    # ================= DASHBOARD =================
    (
        "dashboard_ri",
        1,
        "Section 1",
        "Vision Globale",
        "Vue globale des mobilités internationales des étudiants.",
        """Analyse des mobilités internationales sur 5 ans avec indicateurs clés.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=7c44948851392c8201a6",
        "",
        0,
        "",
        ""
    ),
    (
        "dashboard_ri",
        2,
        "Section 2",
        "Études générales (FISA)",
        "Analyse des mobilités FISA.",
        """Analyse détaillée des étudiants FISA.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=9065243e215d693c7aae",
        "",
        0,
        "",
        ""
    ),
        (
        "dashboard_ri",
        3,
        "Section 3",
        "Études générales (FISE)",
        "Analyse des mobilités FISE.",
        """Analyse détaillée des étudiants FISE.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=0e3141e0203532e39b86",
        "",
        0,
        "",
        ""
    ),
       # ================= BUDGET =================
    (
        "budget_ri",
        1,
        "Section 1",
        "logement FISE",
        "Analyse du logement.",
        """Détails des dépenses par pays.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=6278fe01a00e77751bdc",
        "rapport.pdf",
        0,
        "",
        ""
    ),
        (
        "budget_ri",
        2,
        "Section 2",
        "loyer mensuel",
        "Analyse loyer mensuel.",
        """Détails des dépenses par pays.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=1831caebb80163b8b439",
        "rapport.pdf",
        0,
        "",
        ""
    ),
        (
        "budget_ri",
        3,
        "Section 3",
        "Dépenses alimentaires",
        "Analyse des dépenses alimentaires.",
        """Détails des dépenses par pays.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=b97c693b416990a3330e",
        "rapport.pdf",
        0,
        "",
        ""
    ),
        (
        "budget_ri",
        4,
        "Section 4",
        "frais scolarité",
        "Analyse des frais de scolarité.",
        """Détails des dépenses par pays.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=c6e6ee664d6a566b6b30",
        "rapport.pdf",
        0,
        "",
        ""
    ),
       (
        "budget_ri",
        5,
        "Section 5",
        "budget FISA",
        "Analyse du coût de vie.",
        """Détails des dépenses par pays.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=06e678bf2401ed508045",
        "rapport.pdf",
        0,
        "",
        ""
    ),
       (
        "budget_ri",
        6,
        "Section 6",
        "budget FISE",
        "Analyse du coût de vie.",
        """Détails des dépenses par pays.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=c0713c2498287d05a856",
        "rapport.pdf",
        0,
        "",
        ""
    ),
    # ================= SATISFACTION =================
    (
        "satisfaction_ri",
        1,
        "Section 1",
        "Satisfaction globale",
        "Analyse satisfaction globale.",
        """Vue globale de la satisfaction des étudiants.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=c5648296d683cecb0586",
        "",
        0,
        "",
        ""
    ),
    (
        "satisfaction_ri",
        2,
        "Section 2",
        "Impact",
        "Analyse de l'impact de la mobilité internationale.",
        """Analyse des coûts et dépenses.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=0996f9f6c687ba0a6938",
        "rapport.pdf",
        0,
        "",
        ""
    ),
     (
        "satisfaction_ri",
        3,
        "Section 3",
        "Aspect positifs",
        "Analyse des aspects positifs de la mobilité internationale.",
        """Analyse des coûts et dépenses.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=18fff5b02a7ad83d3db2",
        "rapport.pdf",
        0,
        "",
        ""
    ),

 

    # ================= AMELIORATION =================
    (
        "amelioration_ri",
        1,
        "Section 1",
        "Axes d’amélioration",
        "Suggestions d'amélioration.",
        """Analyse des retours étudiants.""",
        "https://app.powerbi.com/view?r=eyJrIjoiNmFmZTRiYjktNmY2NC00NDRmLTg0MzYtYTQzNmE4NWZjOGY1IiwidCI6IjIzOTdiODg1LWFmZTQtNGJjNy05ZTFlLWU0ODk5ZWY0NGQxYSIsImMiOjh9&pageName=c59fe952a96be7c6a461",
        "",
        0,
        "",
        ""
    ),
]

# =========================
# INSERT
# =========================
cursor.executemany("""
INSERT INTO sections (
    page_name, section_order, section_label, title, caption,
    description, powerbi_link, pdf_file, is_deleted,
    workspace_id, report_id
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", sections_data)

conn.commit()
conn.close()

print("✅ database.db initialisée avec succès")