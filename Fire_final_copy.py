# ══════════════════════════════════════════════════════════════════════════════
# IMPORTS
# ══════════════════════════════════════════════════════════════════════════════

import pandas as pd
import streamlit as st
import base64
import os

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION PAGE
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="Feux de Forêt USA", layout="wide")

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Sommaire")
pages = [
    "Introduction",
    "Conclusion"
]
page = st.sidebar.radio("Pages", pages)
st.sidebar.title("───────")
st.sidebar.title("Coordonnées")
st.sidebar.write("**Nom :** Lévitique MOUSSAVOU")
st.sidebar.write("**Email :** [moussavoujl@yahoo.fr](moussavoujl@yahoo.fr)")

with open("linkedin.png", "rb") as f:
    linkedin_logo = base64.b64encode(f.read()).decode()

st.sidebar.markdown(
    f'''<a href="https://www.linkedin.com/in/levitique-moussavou-90b634137/" target="_blank">
    Levitique   Moussavou   <img src="data:image/png;base64,{linkedin_logo}" width="30" style="vertical-align:middle; margin-right:8px;">     
     </a>''',
    unsafe_allow_html=True
)

st.sidebar.title("──────")
st.sidebar.write("**Liora - Datascientes 2025**")


# ══════════════════════════════════════════════════════════════════════════════
# IMPORT DATASET DEPUIS KAGGLE (API officielle — plus robuste)
# Les identifiants ne sont JAMAIS écrits ici en clair.
# Ils sont lus depuis :
#   - en local  : .streamlit/secrets.toml   (jamais poussé sur GitHub)
#   - en cloud  : Streamlit Cloud > Settings > Secrets
#
# Format attendu dans secrets.toml :
#   [kaggle]
#   username = "ton_username"
#   key = "ta_cle_api"
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Chargement des données depuis Kaggle...")
def load_data():
    """
    Télécharge df_final.csv depuis Kaggle si absent, puis le charge.
    @st.cache_data garantit que ce bloc ne s'exécute qu'une seule fois
    par session (et est réutilisé entre les utilisateurs sur le même serveur).
    """
    # Configure les credentials Kaggle via variables d'environnement
    # (c'est la méthode attendue par la librairie kaggle officielle)
    os.environ['KAGGLE_USERNAME'] = st.secrets["kaggle"]["username"]
    os.environ['KAGGLE_KEY'] = st.secrets["kaggle"]["key"]

    # Import différé : kaggle lit les variables d'environnement
    # au moment de l'import, donc on importe APRÈS les avoir définies
    from kaggle.api.kaggle_api_extended import KaggleApi

    target_file = './data/df_final.csv'

    if not os.path.exists(target_file):
        os.makedirs('./data', exist_ok=True)
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files(
            'levitique/file-project',
            path='./data',
            unzip=True
        )

    df_fires = pd.read_csv(target_file)
    return df_fires


# Chargement réel — toute erreur ici est désormais visible à l'écran
# au lieu de laisser un spinner tourner sans fin.
try:
    df_fires = load_data()
except Exception as e:
    st.error(f"❌ Erreur lors du chargement des données Kaggle : {e}")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — INTRODUCTION
# ══════════════════════════════════════════════════════════════════════════════
if page == pages[0]:
    st.title(" Analyse des Feux de Forêt aux États-Unis (2000–2015)")
    st.write("### I. Présentation du projet")
    st.text("""
    📖 Projet
    Ce projet, réalisé dans le cadre de la formation certifiante Data Analyst (DataScientest),
    vise à analyser et prédire les départs de feux de forêt aux États-Unis (2000–2015).
    Il inclut une exploration approfondie des données, des visualisations interactives,
    ainsi qu'une modélisation prédictive basée sur des modèles de machine learning.

    🎯 Objectifs du projet
    - Explorer les données et identifier les facteurs déclencheurs des feux.
    - Visualiser les corrélations entre les variables explicatives et la variable cible.
    - Construire un modèle prédictif robuste sur la taille ou la gravité des incendies.
    - Développer un Streamlit interactif pour présenter les résultats.

    📂 Datasets utilisés
    - Dataset principal : US Wildfires Dataset (Kaggle) — ~2M d'incendies
    - 🌐 Données démographiques : StatsAmerica (densité, urbanisation, revenu, chômage)
    - 🌦️ Données météo : Open-Meteo (température, précipitations, humidité, vent)
    - 🌿 Données végétation : EPA (types de végétation, caractéristiques, climat)

    🔍 Hypothèses initiales
    Causes humaines  → Accidentelles (négligences, travaux) / Criminelles (incendies volontaires)
    Causes naturelles → Conditions extrêmes (sécheresse, foudre, vent) / Végétation sèche

    Méthodologie
    1️⃣  Exploration (EDA), nettoyage et visualisations.
    2️⃣  Modélisation prédictive (RandomForest, XGBoost, DecisionTree).
    3️⃣  Rapport final + Streamlit interactif.

    🎯 Variable cible : FIRE_SIZE_CLASS (gravité de l'incendie)
    """)

    st.markdown("### 📋 Dictionnaire des variables principales")
    st.dataframe(pd.DataFrame({
        "Variable":    ["FIRE_YEAR", "DISCOVERY_DATE", "STAT_CAUSE_DESCR", "FIRE_SIZE",
                        "FIRE_SIZE_CLASS", "STATE", "LATITUDE", "LONGITUDE"],
        "Description": ["Année de l'incendie", "Date de découverte", "Cause de l'incendie",
                        "Surface brûlée (acres)", "Classe de taille (A→G)", "État américain",
                        "Latitude", "Longitude"],
        "Type":        ["int64", "datetime", "object", "float64", "object", "object", "float64", "float64"],
    }), use_container_width=True, hide_index=True)

    with st.expander("👀 Aperçu des données chargées depuis Kaggle"):
        st.dataframe(df_fires.head(10), use_container_width=True)
        st.caption(f"{len(df_fires):,} lignes au total")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — CONCLUSION
# ══════════════════════════════════════════════════════════════════════════════

if page == pages[1]:
    st.title(" Conclusion générale")
    st.markdown("""

Lorsqu'on plonge dans un dataset de près de **2 millions d'incendies** enregistrés 
sur 15 ans, on s'attend à trouver des tendances claires. Ce projet nous en a livré 
bien plus que cela : une véritable radiographie des feux de forêt américains, avec 
ses surprises, ses confirmations et ses zones d'ombre.

---

###  L'humain, premier responsable

La première conclusion qui s'impose est inconfortable : **nous sommes notre propre 
ennemi**. La majorité des incendies recensés entre 2000 et 2015 trouvent leur origine 
dans des activités humaines — brûlage de déchets mal maîtrisé, incendies criminels, 
négligences diverses. Ce n'est pas la foudre qui menace le plus les forêts américaines, 
c'est l'inattention, parfois la malveillance.

Cela pose une question simple mais fondamentale : si la cause principale est humaine, 
alors la prévention principale doit l'être aussi. Sensibilisation, réglementation, 
surveillance — les leviers existent, encore faut-il les activer.

---

### 📅 Une saisonnalité implacable

Les données ne mentent pas : **de mars à septembre**, les feux explosent. Ce n'est 
pas une surprise en soi, mais voir les courbes de température et d'humidité se 
croiser exactement aux mêmes périodes que les pics d'incendies donne une autre 
dimension à ce qu'on savait intuitivement.

L'été 2006 restera dans les annales avec plus de **110 000 départs de feux** — un 
record sur la période étudiée. Cette année-là, les conditions météo, la végétation 
sèche et l'activité humaine se sont conjuguées dans le pire scénario possible. 
À l'inverse, 2003 affiche l'un des bilans les plus faibles, rappelant que rien n'est 
une fatalité.

---

### 🗺️ Une géographie des risques très inégale

Autre enseignement frappant : **le risque n'est pas réparti équitablement** sur le 
territoire. 21 états concentrent 80 % des départs de feux. La Géorgie, la Californie, 
le Texas — ces noms reviennent sans cesse. Ce sont des états vastes, densément 
végétalisés pour certains, arides pour d'autres, mais tous exposés à une combinaison 
de facteurs qui les rend particulièrement vulnérables.

Cette concentration géographique est en réalité une bonne nouvelle : elle permet de 
**prioriser les ressources** là où elles auront le plus d'impact.

---

### 🌿 La végétation, un facteur aggravant silencieux

Les forêts de feuillus et mixtes sont les plus touchées en volume, mais ce sont les 
**forêts de conifères** qui inquiètent le plus en été : leur résine, leur densité et 
leur sécheresse estivale en font des poudres à canon naturelles. Un feu qui démarre 
dans une pinède en juillet ne ressemble en rien à un feu de broussailles en mars — 
il est plus rapide, plus chaud, plus difficile à contenir.

Les zones désertiques, à l'inverse, brûlent peu mais de façon extrême lorsqu'elles 
s'embrasent. La végétation conditionne non seulement la **fréquence** des feux mais 
aussi leur **intensité** — une nuance que les données de végétation nous ont permis 
de mettre en lumière.

---

### 🤖 Ce que la machine a appris

Les trois modèles testés — Decision Tree, Random Forest et XGBoost — ont tous réussi 
à apprendre des patterns dans les données. Mais XGBoost s'est distingué : meilleure 
précision, meilleure généralisation, moins de surapprentissage.

Ce qui est remarquable, c'est que le modèle arrive à prédire la **gravité d'un 
incendie** en ne connaissant que quelques variables simples : l'année, la cause, le 
mois et l'heure de découverte. Cela signifie que la gravité d'un feu n'est pas 
aléatoire — elle suit des logiques que l'algorithme a su identifier là où l'œil humain 
aurait eu du mal à les voir dans 2 millions de lignes.

La **cause du feu** et le **mois de découverte** sont ressortis comme les variables 
les plus déterminantes. Autrement dit : *quand* et *pourquoi* un feu démarre prédit 
souvent *à quel point* il sera grave.

---

### 🔭 Et demain ?

Ce projet ouvre des pistes concrètes. Intégrer des données satellitaires de végétation 
en temps réel, croiser avec les indices de sécheresse, ajouter la vitesse et la 
direction du vent — autant d'enrichissements qui permettraient de passer d'un modèle 
*rétrospectif* à un outil *prédictif* opérationnel.

L'objectif final n'est pas de construire un beau dashboard, mais de donner aux 
gestionnaires de forêts, aux pompiers et aux élus un outil d'aide à la décision 
capable de dire : **"Attention, les conditions réunies aujourd'hui ressemblent à celles 
des pires étés enregistrés."**

---

> *"Les données ne peuvent pas éteindre les feux. Mais elles peuvent nous aider à 
> ne pas les allumer."*
""")