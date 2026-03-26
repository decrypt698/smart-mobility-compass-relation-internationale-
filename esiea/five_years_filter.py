import re
import numpy as np
import pandas as pd
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_distances
from transformers import pipeline


def generer_top_commentaires(fichier_entree, fichier_sortie):
    # =========================
    # PARAMÈTRES
    # =========================
    FICHIER = fichier_entree

    COL_INSTITUTION = "Institution_accueil"
    COL_DATE_DEBUT = "debut_periode_echange"
    COLONNES_TEXTES = ["aspect_positif", "aspect_ameliorer", "conseils"]

    TOP_K = 10
    EPS_CANDIDATS = [0.28, 0.30, 0.32]
    MIN_SAMPLES = 2

    EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
    SENTIMENT_MODEL = "nlptown/bert-base-multilingual-uncased-sentiment"

    # =========================
    # 1) LECTURE
    # =========================
    df = pd.read_excel(FICHIER)
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(" ", "_", regex=False)
    )

    for c in [COL_INSTITUTION, COL_DATE_DEBUT] + COLONNES_TEXTES:
        if c not in df.columns:
            raise ValueError(f"Colonne introuvable dans Excel: {c}\nColonnes trouvées: {df.columns.tolist()}")

    # =========================
    # 1bis) FILTRE 5 DERNIÈRES ANNÉES
    # =========================
    s_date = df[COL_DATE_DEBUT]
    dt = pd.to_datetime(s_date, errors="coerce", dayfirst=True)
    year_from_dt = dt.dt.year
    year_from_text = pd.to_numeric(
        s_date.astype(str).str.extract(r"(\d{4})")[0],
        errors="coerce"
    )

    df["__annee_debut__"] = year_from_dt.fillna(year_from_text)

    if df["__annee_debut__"].isna().all():
        raise ValueError(
            f"Impossible d'extraire une année depuis la colonne {COL_DATE_DEBUT}. "
            "Vérifie le format (ex: 2023-06-30 ou 2023)."
        )

    max_year = int(df["__annee_debut__"].max())
    min_year = max_year - 4

    df = df[df["__annee_debut__"].between(min_year, max_year)].copy()

    # =========================
    # 2) FORMAT LONG
    # =========================
    df_long = df[[COL_INSTITUTION] + COLONNES_TEXTES].melt(
        id_vars=[COL_INSTITUTION],
        value_vars=COLONNES_TEXTES,
        var_name="question",
        value_name="texte"
    )

    # =========================
    # 3) NETTOYAGE
    # =========================
    def clean_text(x) -> str:
        if pd.isna(x):
            return ""
        s = str(x).strip()
        if s.lower() == "x":
            return ""
        return s

    df_long["texte_clean"] = df_long["texte"].apply(clean_text)
    df_long = df_long[df_long["texte_clean"].str.len() > 0].reset_index(drop=True)

    # =========================
    # 4) FILTRE "NEUTRE PHRASE"
    # =========================
    NEUTRES_REGEX = re.compile(
        r"\b("
        r"ras|r\.a\.s|ok|okay|oui|non|bof|meh|"
        r"rien|néant|neant|aucun|aucune|aucuns|aucunes|"
        r"rien\s*(a|à)\s*dire|rien\s*(a|à)\s*ajouter|rien\s*(a|à)\s*signaler|"
        r"aucune?\s*remarque|aucune?\s*am[eé]lioration|aucun\s*changement|aucun\s*avis|"
        r"pas\s*de\s*commentaire|pas\s*d['’]avis|sans\s*avis|aucun\s*commentaire|"
        r"tout\s*est\s*bien|tout\s*va\s*bien|rien\s*(a|à)\s*changer|aucun\s*probl[eè]me|aucun\s*souci|"
        r"n/a|na|none|null|vide|"
        r"je\s*ne\s*sais\s*pas|je\s*n['’]ai\s*pas\s*d['’]id[eé]e|aucune?\s*id[eé]e"
        r")\b",
        re.IGNORECASE
    )

    def est_neutre_phrase(texte: str) -> bool:
        if not texte or len(texte.strip()) < 3:
            return True
        t = texte.strip().lower()
        if t in {"ok", "oui", "non", "-", "--", ".", "...", ","}:
            return True
        return bool(NEUTRES_REGEX.search(t))

    df_long["neutre_phrase"] = df_long["texte_clean"].apply(est_neutre_phrase)

    # =========================
    # 5) SENTIMENT + HEURISTIQUE
    # =========================
    sentiment_model = pipeline("sentiment-analysis", model=SENTIMENT_MODEL)

    def get_sentiment(texte: str) -> str:
        if not texte or len(texte.strip()) < 3:
            return "neutre"
        res = sentiment_model(texte[:512])[0]
        stars = int(res["label"].split()[0])
        if stars <= 2:
            return "negatif"
        elif stars == 3:
            return "neutre"
        else:
            return "positif"

    df_long["sentiment"] = df_long["texte_clean"].apply(get_sentiment)

    NEG_WORDS = re.compile(
        r"\b(probl[eè]me|difficile|manque|absen|nul|mauvais|décevant|déception|"
        r"insuffisant|pas\s+assez|trop\s+peu|désorganis|retard)\b",
        re.IGNORECASE
    )
    POS_WORDS = re.compile(
        r"\b(super|excellent|génial|top|parfait|bien|incroyable|utile|"
        r"intéressant|bienveillant|à\s+l['’]écoute|satisfait)\b",
        re.IGNORECASE
    )

    def force_keywords(row):
        s = row["sentiment"]
        t = row["texte_clean"]
        q = row["question"]
        if q == "aspect_ameliorer" and NEG_WORDS.search(t):
            return "negatif"
        if q == "aspect_positif" and POS_WORDS.search(t):
            return "positif"
        return s

    df_long["sentiment"] = df_long.apply(force_keywords, axis=1)

    # =========================
    # 6) FILTRAGE
    # =========================
    df_long = df_long[~df_long["neutre_phrase"]].copy()
    df_long = df_long[~((df_long["question"] == "aspect_ameliorer") & (df_long["sentiment"] != "negatif"))].copy()
    df_long = df_long[~((df_long["question"] == "aspect_positif") & (df_long["sentiment"] != "positif"))].copy()
    df_long = df_long[~((df_long["question"] == "conseils") & (df_long["sentiment"] == "neutre"))].copy()

    df_long = df_long.reset_index(drop=True)
    if df_long.empty:
        raise ValueError("Après filtrage, il ne reste plus de texte. Vérifie tes données / règles.")

    # =========================
    # 7) EMBEDDINGS
    # =========================
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    emb = embedder.encode(df_long["texte_clean"].tolist(), show_progress_bar=True)
    emb = normalize(emb)

    # =========================
    # 8) TOP K PAR (Institution × question)
    # =========================
    results = []

    for (inst, question), idx in df_long.groupby([COL_INSTITUTION, "question"]).groups.items():
        idx = np.array(list(idx), dtype=int)
        texts = df_long.loc[idx, "texte_clean"].tolist()
        E = emb[idx]

        best_eps, best_score = EPS_CANDIDATS[0], -1
        for eps_try in EPS_CANDIDATS:
            labels_try = DBSCAN(eps=eps_try, min_samples=MIN_SAMPLES, metric="cosine").fit_predict(E)
            score = int(np.sum(labels_try != -1))
            if score > best_score:
                best_score, best_eps = score, eps_try

        labels = DBSCAN(eps=best_eps, min_samples=MIN_SAMPLES, metric="cosine").fit_predict(E)

        unique, counts = np.unique(labels, return_counts=True)
        clusters = [(lab, int(cnt)) for lab, cnt in zip(unique, counts) if lab != -1]
        clusters.sort(key=lambda x: x[1], reverse=True)

        rank = 1

        for lab, cnt in clusters:
            if rank > TOP_K:
                break
            cluster_pos = np.where(labels == lab)[0]
            vecs = E[cluster_pos]
            centre = vecs.mean(axis=0, keepdims=True)
            dists = cosine_distances(centre, vecs)[0]
            rep_local = cluster_pos[int(np.argmin(dists))]
            rep_text = texts[int(rep_local)]

            results.append({
                "Institution_accueil": inst,
                "question": question,
                "rang": rank,
                "frequence": cnt,
                "commentaire_representatif": rep_text,
            })
            rank += 1

        if rank <= TOP_K:
            noise_pos = np.where(labels == -1)[0]
            if len(noise_pos) > 0:
                global_centre = E.mean(axis=0, keepdims=True)
                noise_dists = cosine_distances(global_centre, E[noise_pos])[0]
                noise_pos = noise_pos[np.argsort(noise_dists)]

            for p in noise_pos:
                if rank > TOP_K:
                    break
                results.append({
                    "Institution_accueil": inst,
                    "question": question,
                    "rang": rank,
                    "frequence": 1,
                    "commentaire_representatif": texts[int(p)],
                })
                rank += 1

    summary = pd.DataFrame(results)

    # =========================
    # 9) FORMAT FINAL EXCEL
    # =========================
    wide = summary.pivot_table(
        index=["Institution_accueil", "rang"],
        columns="question",
        values=["commentaire_representatif", "frequence"],
        aggfunc="first"
    )

    wide.columns = [f"{q}_{v}" for v, q in wide.columns]
    wide = wide.reset_index()

    wide = wide.rename(columns={
        "Institution_accueil": "Institution_accueil",
        "rang": "rank",
        "aspect_positif_commentaire_representatif": "aspect_positif",
        "aspect_positif_frequence": "frequence_aspect_positif",
        "aspect_ameliorer_commentaire_representatif": "aspect_ameliorer",
        "aspect_ameliorer_frequence": "frequence_aspect_ameliorer",
        "conseils_commentaire_representatif": "conseils",
        "conseils_frequence": "frequence_conseils",
    })

    for col in [
        "aspect_positif", "frequence_aspect_positif",
        "aspect_ameliorer", "frequence_aspect_ameliorer",
        "conseils", "frequence_conseils",
    ]:
        if col not in wide.columns:
            wide[col] = np.nan

    wide["aspect_positif"] = wide["aspect_positif"].fillna("aucun commentaire")
    wide["aspect_ameliorer"] = wide["aspect_ameliorer"].fillna("aucun commentaire")
    wide["conseils"] = wide["conseils"].fillna("aucun commentaire")

    wide["frequence_aspect_positif"] = wide["frequence_aspect_positif"].fillna(0).astype(int)
    wide["frequence_aspect_ameliorer"] = wide["frequence_aspect_ameliorer"].fillna(0).astype(int)
    wide["frequence_conseils"] = wide["frequence_conseils"].fillna(0).astype(int)

    wide = wide[[
        "Institution_accueil", "rank",
        "aspect_positif", "frequence_aspect_positif",
        "aspect_ameliorer", "frequence_aspect_ameliorer",
        "conseils", "frequence_conseils",
    ]].sort_values(["Institution_accueil", "rank"])

    # =========================
    # 10) EXPORT EXCEL
    # =========================
    with pd.ExcelWriter(fichier_sortie, engine="openpyxl") as writer:
        wide.to_excel(writer, sheet_name="resultat_final", index=False)

    print(f"\nOK: {fichier_sortie} généré")