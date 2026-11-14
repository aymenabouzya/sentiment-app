"""Page Streamlit de présentation uniquement (TP5)."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ui import client  # noqa: E402

st.set_page_config(page_title="Analyse de sentiment", page_icon="💬", layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 8% 0%, rgba(196, 231, 220, 0.30), transparent 34rem),
            #f5f7f8;
        color: #172b3a;
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    .block-container {
        max-width: 1080px;
        padding: 3.25rem 2rem 5rem;
    }
    .eyebrow {
        color: #167c68;
        font-size: 0.76rem;
        font-weight: 750;
        letter-spacing: 0.13em;
        margin-bottom: 0.55rem;
        text-transform: uppercase;
    }
    h1 {
        color: #172b3a;
        font-size: 2.55rem !important;
        letter-spacing: -0.045em;
        margin-bottom: 0.35rem !important;
    }
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] h4 {
        color: #172b3a;
    }
    .hero-copy {
        color: #62727d;
        font-size: 1.05rem;
        margin: 0 0 1.25rem;
    }
    [data-testid="stCaptionContainer"] {
        color: #526a76;
        font-size: 0.88rem;
    }
    [data-testid="stAppViewContainer"] [data-testid="stTextArea"] label,
    [data-testid="stAppViewContainer"] [data-testid="stFileUploader"] label {
        color: #344b59;
    }
    [data-testid="stTabs"] [role="tablist"] {
        background: #e9eff0;
        border: 1px solid #e1e8e8;
        border-radius: 12px;
        gap: 0.4rem;
        padding: 0.35rem;
    }
    [data-testid="stTabs"] button[role="tab"] {
        border-radius: 9px;
        color: #536873;
        font-weight: 600;
        padding: 0.55rem 1rem;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: #fff;
        box-shadow: 0 1px 3px rgba(23, 43, 58, 0.10);
        color: #176f60;
    }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background: transparent;
    }
    [data-testid="stTabs"] [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid #e6ebed;
        border-radius: 16px;
        box-shadow: 0 8px 28px rgba(23, 43, 58, 0.045);
        margin-top: 1rem;
        padding: 1.15rem 1.25rem;
    }
    [data-testid="stTextArea"] textarea {
        background: #fbfcfc;
        border: 1px solid #dce5e7;
        border-radius: 10px;
        caret-color: #167c68;
        color: #172b3a;
        line-height: 1.65;
        -webkit-text-fill-color: #172b3a;
    }
    [data-testid="stTextArea"] textarea::placeholder {
        color: #71818a;
        -webkit-text-fill-color: #71818a;
    }
    [data-testid="stTextArea"] textarea:focus {
        border-color: #268875;
        box-shadow: 0 0 0 2px rgba(38, 136, 117, 0.14);
    }
    [data-testid="stFileUploader"] section {
        background: #fbfcfc;
        border: 1px dashed #bdcecf;
        border-radius: 12px;
    }
    .stButton > button,
    [data-testid="stDownloadButton"] > button {
        border-radius: 9px;
        font-weight: 650;
        min-height: 2.8rem;
        transition: transform 120ms ease, box-shadow 120ms ease;
    }
    .stButton > button[kind="primary"] {
        background: #167c68;
        border: 1px solid #167c68;
    }
    .stButton > button:hover,
    [data-testid="stDownloadButton"] > button:hover {
        box-shadow: 0 4px 12px rgba(23, 43, 58, 0.12);
        transform: translateY(-1px);
    }
    [data-testid="stMetric"] {
        background: #fff;
        border: 1px solid #e6ebed;
        border-radius: 12px;
        box-shadow: 0 3px 12px rgba(23, 43, 58, 0.035);
        padding: 1rem 1.1rem;
    }
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #172b3a;
    }
    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #526a76;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid #e6ebed;
        border-radius: 10px;
        overflow: hidden;
    }
    @media (max-width: 640px) {
        .block-container {
            padding: 2rem 1rem 3rem;
        }
        h1 {
            font-size: 2rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="eyebrow">Analyse intelligente des avis</div>', unsafe_allow_html=True)
st.title("Analyse de sentiment des avis")
st.markdown(
    '<p class="hero-copy">Un avis client, un verdict clair. Collez un texte ou importez un fichier CSV.</p>',
    unsafe_allow_html=True,
)

session = client.creer_session()
etat = client.sante(session)
if not etat.ok:
    st.error(etat.message)

onglet_avis, onglet_lot = st.tabs(["Un avis", "Un fichier d'avis"])

with onglet_avis:
    with st.container(border=True):
        st.markdown("#### Analyse individuelle")
        st.caption("Décrivez le ressenti exprimé dans un avis client.")
        texte = st.text_area("Avis client", placeholder="Ex. : Livraison rapide, produit conforme, très satisfait…", height=150)
        if st.button("Analyser l'avis", type="primary", use_container_width=True):
            reponse = client.predire(session, texte)
            if reponse.ok and reponse.label is not None and reponse.score is not None:
                st.metric(client.VERDICTS[reponse.label], f"{reponse.score:.0%}")
                st.caption("Score de confiance du modèle")
            elif reponse.message == client.REFUS:
                st.warning(reponse.message)
            else:
                st.error(reponse.message)

with onglet_lot:
    with st.container(border=True):
        st.markdown("#### Analyse par fichier")
        st.caption("Importez un CSV contenant une colonne nommée `text`.")
        fichier = st.file_uploader("Fichier CSV", type="csv", label_visibility="collapsed")
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
                avis["confiance"] = [
                    f"{reponse.score:.0%}" if reponse.score is not None else ""
                    for reponse in reponses
                ]
                resume = client.resumer(reponses)
                total = sum(resume.values())
                positifs, negatifs, telecharges = st.columns(3)
                positifs.metric("Avis positifs", resume["POSITIVE"])
                negatifs.metric("Avis négatifs", resume["NEGATIVE"])
                telecharges.metric("Avis analysés", total)
                st.dataframe(avis, use_container_width=True, hide_index=True)
                st.download_button(
                    "Télécharger les résultats",
                    avis.to_csv(index=False),
                    file_name="resultats.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
