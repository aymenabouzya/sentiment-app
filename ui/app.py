"""Page Streamlit de présentation uniquement (TP5)."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ui import client  # noqa: E402

st.set_page_config(page_title="Analyse de sentiment")

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: Georgia, "Times New Roman", serif;
        color: #20262e;
    }
    .stApp {
        background: #ffffff;
    }
    section[data-testid="stMain"] > div {
        max-width: 1200px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    h1 {
        font-family: Georgia, "Times New Roman", serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        margin: 0 0 0.55rem 0 !important;
    }
    .stCaptionContainer {
        font-size: 0.95rem;
        color: #6e76a0;
        margin-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.8rem;
        border-bottom: 1px solid #e3e4e8;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.15rem;
        padding-left: 0;
        padding-right: 0;
        height: 2.8rem;
    }
    .stTabs [aria-selected="true"] {
        color: #2464a0 !important;
        border-bottom-color: #2464a0 !important;
    }
    label, .stTextArea label p, .stFileUploader label p {
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1rem !important;
    }
    textarea, [data-testid="stFileUploaderDropzone"] {
        font-family: Georgia, "Times New Roman", serif !important;
        border-radius: 6px !important;
        background: #ffffff !important;
    }
    .stTextArea textarea {
        min-height: 58px;
        font-size: 1rem !important;
        border-color: #c4c7cf;
    }
    .stButton > button {
        font-family: Georgia, "Times New Roman", serif;
        color: #20262e;
        background: #ffffff;
        border: 1px solid #2464a0;
        border-radius: 6px;
        min-height: 38px;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }
    .stButton > button:hover {
        border-color: #2464a0;
        color: #2464a0;
        background: #f8fbfe;
    }
    [data-testid="stMetricLabel"] {
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1rem;
        color: #20262e;
    }
    [data-testid="stMetricValue"] {
        font-family: Georgia, "Times New Roman", serif;
        font-size: 2rem;
        color: #20262e;
    }
    [data-testid="stDataFrame"] {
        border: none;
        font-family: Georgia, "Times New Roman", serif;
    }
    [data-testid="stFileUploaderDropzone"] {
        min-height: 58px;
    }
    header[data-testid="stHeader"] {
        height: 0;
    }
    #MainMenu, footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Analyse de sentiment des avis")

session = client.creer_session()
etat = client.sante(session)
if etat.ok:
    st.caption(f"API prête : {etat.message}")
else:
    st.error(etat.message)

onglet_avis, onglet_lot = st.tabs(["Un avis", "Un fichier d'avis"])

with onglet_avis:
    texte = st.text_area("Avis client")
    if st.button("Analyser"):
        reponse = client.predire(session, texte)
        if reponse.ok and reponse.label is not None and reponse.score is not None:
            st.metric(client.VERDICTS[reponse.label], f"{reponse.score:.0%}")
            if reponse.label == "INDETERMINE":
                st.info("La confiance est sous le seuil d'abstention : un humain doit trancher.")
        elif reponse.message == client.REFUS:
            st.warning(reponse.message)
        else:
            st.error(reponse.message)

with onglet_lot:
    fichier = st.file_uploader("Fichier CSV avec une colonne text", type="csv")
    if fichier is not None:
        avis = pd.read_csv(fichier)
        if "text" not in avis.columns:
            st.error("Colonne text absente du fichier.")
        else:
            reponses = client.predire_lot(session, avis["text"].astype(str).tolist())
            avis["verdict"] = [
                client.VERDICTS[r.label] if r.ok and r.label else r.message
                for r in reponses
            ]
            avis["confiance"] = [r.score for r in reponses]
            st.dataframe(avis, use_container_width=True)
            st.write(client.resumer(reponses))
            st.download_button(
                "Télécharger les résultats",
                avis.to_csv(index=False),
                file_name="resultats.csv",
                mime="text/csv",
            )
