from types import SimpleNamespace
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import streamlit as st

# === ELEMENTS DE DECISION POUR RECOMMANDATION
# -- Poids des indicateurs et des catégories --
data_poids = [
    # --- Profil PRUDENT ---
    ("prudent", "dynamique", "Delta MA50",        0.15, 0.20),
    ("prudent", "dynamique", "Delta ATH",         0.10, 0.20),
    ("prudent", "dynamique", "Delta cours moyen", 0.20, 0.20),
    ("prudent", "dynamique", "Evol CA 0y",        0.25, 0.20),
    ("prudent", "dynamique", "Evol CA +1y",       0.03, 0.20),
    ("prudent", "dynamique", "Evol EPS 0y",       0.25, 0.20),
    ("prudent", "dynamique", "Evol EPS +1y",      0.02, 0.20),
    ("prudent", "gains", "Div %",     0.50, 0.30),
    ("prudent", "gains", "Rendement", 0.30, 0.30),
    ("prudent", "gains", "Potentiel", 0.20, 0.30),
    ("prudent", "risques", "Volatilité",        0.50, 0.50),
    ("prudent", "risques", "Delta cours moyen", 0.25, 0.50),
    ("prudent", "risques", "Delta MA50",        0.15, 0.50),
    ("prudent", "risques", "Delta ATH",         0.10, 0.50),
    # --- Profil ÉQUILIBRÉ ---
    ("équilibré", "dynamique", "Delta MA50",        0.15, 0.40),
    ("équilibré", "dynamique", "Delta ATH",         0.10, 0.40),
    ("équilibré", "dynamique", "Delta cours moyen", 0.20, 0.40),
    ("équilibré", "dynamique", "Evol CA 0y",        0.20, 0.40),
    ("équilibré", "dynamique", "Evol CA +1y",       0.10, 0.40),
    ("équilibré", "dynamique", "Evol EPS 0y",       0.20, 0.40),
    ("équilibré", "dynamique", "Evol EPS +1y",      0.05, 0.40),
    ("équilibré", "gains", "Div %",     0.35, 0.35),
    ("équilibré", "gains", "Rendement", 0.35, 0.35),
    ("équilibré", "gains", "Potentiel", 0.30, 0.35),
    ("équilibré", "risques", "Volatilité",        0.40, 0.25),
    ("équilibré", "risques", "Delta cours moyen", 0.30, 0.25),
    ("équilibré", "risques", "Delta MA50",        0.20, 0.25),
    ("équilibré", "risques", "Delta ATH",         0.10, 0.25),
    # --- Profil DYNAMIQUE ---
    ("dynamique", "dynamique", "Delta MA50",        0.20, 0.50),
    ("dynamique", "dynamique", "Delta ATH",         0.15, 0.50),
    ("dynamique", "dynamique", "Delta cours moyen", 0.10, 0.50),
    ("dynamique", "dynamique", "Evol CA 0y",        0.03, 0.50),
    ("dynamique", "dynamique", "Evol CA +1y",       0.25, 0.50),
    ("dynamique", "dynamique", "Evol EPS 0y",       0.02, 0.50),
    ("dynamique", "dynamique", "Evol EPS +1y",      0.25, 0.50),
    ("dynamique", "gains", "Div %",     0.20, 0.35),
    ("dynamique", "gains", "Rendement", 0.30, 0.35),
    ("dynamique", "gains", "Potentiel", 0.50, 0.35),
    ("dynamique", "risques", "Volatilité",        0.30, 0.15),
    ("dynamique", "risques", "Delta cours moyen", 0.15, 0.15),
    ("dynamique", "risques", "Delta MA50",        0.25, 0.15),
    ("dynamique", "risques", "Delta ATH",         0.30, 0.15),
]
df_poids = pd.DataFrame(data_poids, columns=["profil", "categorie", "indicateur", "poids_indicateur", "poids_categorie"])
# -- Seuils de performance --
data_seuils = [
    # --- Profil PRUDENT ---
    ("prudent", "Div %",        0.02, 0.04, 0.01, 0.06),
    ("prudent", "Rendement",   0.02, 0.10, 0.00, 0.20),
    ("prudent", "Volatilité",  0.10, 0.20, 0.00, 0.40),
    ("prudent", "Delta cours moyen", -0.03, 0.03, -0.10, 0.10),
    ("prudent", "Delta MA50", -0.02, 0.02, -0.05, 0.05),
    ("prudent", "Delta ATH",  -0.15, -0.05, -0.25, 0.00),
    ("prudent", "Evol CA 0y",  0.01, 0.05, 0.00, 0.10),
    ("prudent", "Evol CA +1y",  0.02, 0.06, 0.00, 0.12),
    ("prudent", "Evol EPS 0y",  0.02, 0.07, 0.00, 0.15),
    ("prudent", "Evol EPS +1y",  0.03, 0.08, 0.00, 0.15),
    ("prudent", "Potentiel",  0.03, 0.10, 0.00, 0.20),
    # --- Profil ÉQUILIBRÉ ---
    ("équilibré", "Div %",        0.02, 0.06, 0.01, 0.08),
    ("équilibré", "Rendement",   0.05, 0.15, -0.10, 0.30),
    ("équilibré", "Volatilité",  0.10, 0.25, 0.00, 0.50),
    ("équilibré", "Delta cours moyen", -0.05, 0.08, -0.15, 0.15),
    ("équilibré", "Delta MA50", -0.05, 0.05, -0.10, 0.10),
    ("équilibré", "Delta ATH",  -0.20, -0.10, -0.40, 0.10),
    ("équilibré", "Evol CA 0y",  0.03, 0.08, -0.02, 0.15),
    ("équilibré", "Evol CA +1y",  0.04, 0.10, -0.03, 0.18),
    ("équilibré", "Evol EPS 0y",  0.04, 0.12, -0.05, 0.25),
    ("équilibré", "Evol EPS +1y",  0.05, 0.15, -0.05, 0.25),
    ("équilibré", "Potentiel",  0.05, 0.15, -0.05, 0.30),
    # --- Profil DYNAMIQUE ---
    ("dynamique", "Div %",        0.00, 0.03, 0.00, 0.08),
    ("dynamique", "Rendement",   0.10, 0.30, -0.20, 0.60),
    ("dynamique", "Volatilité",  0.20, 0.40, 0.0, 0.80),
    ("dynamique", "Delta cours moyen", -0.10, 0.15, -0.20, 0.25),
    ("dynamique", "Delta MA50", -0.10, 0.10, -0.10, 0.20),
    ("dynamique", "Delta ATH",  -0.25, -0.05, -0.55, 0.25),
    ("dynamique", "Evol CA 0y",  0.05, 0.12, -0.05, 0.20),
    ("dynamique", "Evol CA +1y",  0.08, 0.20, -0.05, 0.30),
    ("dynamique", "Evol EPS 0y",  0.08, 0.25, -0.10, 0.40),
    ("dynamique", "Evol EPS +1y",  0.10, 0.30, -0.10, 0.50),
    ("dynamique", "Potentiel",  0.10, 0.25, -0.10, 0.40),
]
df_seuils = pd.DataFrame(data_seuils, columns=["profil", "indicateur", "obj_min", "obj_max", "cat_min", "cat_max"])
# -- Intervalles de recommandation --
data_intervals = [
    ("strongBuy", 0.00, 0.20, 1),
    ("buy", 0.20, 0.40, 1),
    ("hold", 0.40, 0.60, 0),
    ("sell", 0.60, 0.80, -1),
    ("strongSell", 0.80, 1.01, -1)]
df_intervals = pd.DataFrame(data_intervals, columns=["Recommandation", "score_min", "score_max", "Sens_confiance"])
smiley_map = {-2: "😭", -1: "😟", 0: "😐", 1: "🙂", 2: "😄"}
                       
# === FONCTIONS DE CALCUL ===
# -- Fonction de chargement de la liste des actions --
def charger_tickers_euronext_paris(file="data/Euronext_Equities.csv"):
    df = pd.read_csv(file, sep=';')
    df = df[['Name', 'ISIN', 'Symbol']]
    df = df.copy()
    df = df[df['Symbol'].notna()]
    df = df.reset_index(drop=True)
    df['Ticker'] = df['Symbol'].astype(str) + ".PA"
    return df
# -- Fonctions de traduction des données en risque --
def div_risk_level(div):
    if div <= 0.02:
        return "🟡"
    elif div <= 0.06:
        return "🟢"
    else:
        return "🔴"
def rdt_risk_level(rdt):
    if rdt < 0.05:
        return "🔴"
    elif rdt < 0.15:
        return "🟡"
    else:
        return "🟢"
def vol_risk_level(vol):
    if vol < 0.15:
        return "🟢"
    elif vol < 0.30:
        return "🟡"
    else:
        return "🔴"
# -- Fonction de chargement des données financières --
def charge_donnees_bourse(ticker):
    action_suivie = yf.Ticker(ticker)
    # Intraday : 1 jour si dispo, sinon 2 jours
    day_vue1 = action_suivie.history(period="1d", interval="1m")
    day_vue2 = action_suivie.history(period="2d", interval="1m")
    day_vue = day_vue1 if len(day_vue1) > 0 else day_vue2
    day_vue = day_vue.sort_index()
    # Historique 2 ans
    historique = action_suivie.history(period="2y", interval="1d").sort_index()
    historique["prev_close"] = historique["Close"].shift(1)
    historique["MA20"] = historique["Close"].rolling(20).mean()
    historique["MA50"] = historique["Close"].rolling(50).mean()
    historique["support"] = historique["Low"].rolling(50).min()
    historique["resistance"] = historique["High"].rolling(50).max()
    # Vue 1 an : restriction de l'historique sur 1 après calcul des indicateurs mobiles
    year_vue = historique.loc[historique.index >= historique.index.max() - pd.Timedelta(days=365)]
    # Calcul des indicateurs de performance
    indicateurs = pd.DataFrame(index=[0])
    indicateurs['MA50'] = year_vue['MA50'].iloc[-1]    
    indicateurs['Delta MA50'] = (year_vue['Close'].iloc[-1] / year_vue['MA50'].iloc[-1] - 1 if year_vue['MA50'].iloc[-1] != 0 else None)
    indicateurs['ATH / 1 an'] = year_vue['Close'].max()
    indicateurs['Delta ATH'] = (year_vue['Close'].iloc[-1] / year_vue['Close'].max() - 1 if year_vue['Close'].max() != 0 else None)
    indicateurs['Cours moyen / 1 an'] = year_vue['Close'].mean()
    indicateurs['Delta cours moyen'] = (year_vue['Close'].iloc[-1] / year_vue['Close'].mean() - 1 if year_vue['Close'].max() != 0 else None)
    indicateurs['Dividendes'] = year_vue['Dividends'].sum()
    indicateurs['Div %'] = indicateurs.apply(lambda row: row['Dividendes'] / row['Cours moyen / 1 an'] if row['Cours moyen / 1 an'] != 0 else None, axis=1)
    indicateurs['Rendement'] = (year_vue['Close'].iloc[-1] / year_vue['Close'].iloc[0] - 1 if year_vue['Close'].iloc[0] != 0 else None)
    rendements_jours = year_vue['Close'].pct_change().dropna()
    indicateurs['Volatilité'] = rendements_jours.std() * (252 ** 0.5)
    indicateurs['Evol CA 0y'] = action_suivie.revenue_estimate.loc["0y", "growth"]
    indicateurs['Evol CA +1y'] = action_suivie.revenue_estimate.loc["+1y", "growth"]
    indicateurs['Evol EPS 0y'] = action_suivie.earnings_estimate.loc["0y", "growth"]
    indicateurs['Evol EPS +1y'] = action_suivie.earnings_estimate.loc["+1y", "growth"]
    indicateurs['Potentiel'] = action_suivie.analyst_price_targets['mean'] / action_suivie.analyst_price_targets['current'] -1
    # Traduction des indicateurs en risque ou opportunité
    risque = pd.DataFrame(index=[0])
    risque['Div %'] = indicateurs['Div %'].apply(div_risk_level)
    risque['Rendement'] = indicateurs['Rendement'].apply(rdt_risk_level)
    risque['Volatilité'] = indicateurs['Volatilité'].apply(vol_risk_level)
    return SimpleNamespace(action_suivie = action_suivie, day_vue = day_vue, year_vue = year_vue, indicateurs = indicateurs, risque = risque)
# -- Fonctions de calcul des scores de performance --
def safe_get_value(df, col): # Sécurisation de la présence d'un indicateur
    try:
        return df.iloc[0][col]
    except KeyError:
        return None
def score(val, obj_min, obj_max, cat_min, cat_max): # Normalisation de la valeur d'un indicateur
    #Retourne un score entre 0 et 1 représentant la distance entre un indicateur et sa zone objectif (0) ou catastrophique (1).
    # Vérification de cohérence des bornes
    if not (cat_min <= obj_min <= obj_max <= cat_max):
        raise ValueError(f"Incohérence dans les bornes reçues : cat_min={cat_min}, obj_min={obj_min}, obj_max={obj_max}, cat_max={cat_max}")
    # 1. Zone idéale → score = 0
    if obj_min <= val <= obj_max:
        return 0.0
    # 2. Zone catastrophique → score = 1
    if val <= cat_min or val >= cat_max:
        return 1.0
    # 3. Zone intermédiaire → interpolation linéaire
    if val < obj_min: # Cas inférieur à l'objectif
        return (obj_min - val) / (obj_min - cat_min)
    if val > obj_max: # Cas supérieur à l'objectif
        return (val - obj_max) / (cat_max - obj_max)
    # Sécurité (ne devrait jamais arriver)
    return None
def score_categorie(df_scores, df_poids): # Calcul des scores agrégés par catégorie d'indicateurs
    # Jointure sur profil + indicateur
    merged = df_scores.merge(df_poids, on=["profil", "indicateur"], how="left")
    # Score pondéré par indicateur
    merged["score_indicateur_pondere"] = merged["score"] * merged["poids_indicateur"]
    # Score par catégorie = somme des scores pondérés
    score_cat = merged.groupby(["profil", "categorie"], as_index=False)["score_indicateur_pondere"].sum()
    # Renommage
    score_cat.rename(columns={"score_indicateur_pondere": "score_categorie"}, inplace=True)
    return score_cat
def score_global(df_score_cat, df_poids): # Calcul des scores globaux
    # Jointure pour récupérer les poids de catégorie
    merged = df_score_cat.merge(df_poids[["profil", "categorie", "poids_categorie"]].drop_duplicates(), on=["profil", "categorie"], how="left")
    # Score global pondéré
    merged["score_global_part"] = merged["score_categorie"] * merged["poids_categorie"]
    # Agrégation finale
    score_glob = merged.groupby("profil", as_index=False)["score_global_part"].sum()
    score_glob.rename(columns={"score_global_part": "score_global"}, inplace=True)
    # Ajout recommandation
    score_glob = score_to_reco(score_glob, df_intervals)
    # Tri selon profil d'investisseur
    ordre_profils = ["prudent", "équilibré", "dynamique"]
    score_glob["profil"] = pd.Categorical(score_glob["profil"], categories=ordre_profils, ordered=True)
    score_glob = score_glob.sort_values("profil").reset_index(drop=True)
    return score_glob
def score_to_reco(df_score, df_inter): # Traduction des scores en recommandations
    df = df_score.merge(df_inter, how='cross')
    df = df.loc[(df['score_global'] >= df['score_min']) & (df['score_global'] < df['score_max'])]
    df["Confiance"] = 0 + df['Sens_confiance']  # valeur par défaut
    df.loc[df["score_global"] <= df["score_min"] + 0.05, "Confiance"] = 1 + df['Sens_confiance']
    df.loc[df["score_global"] >= df["score_max"] - 0.05, "Confiance"] = -1 + df['Sens_confiance']
    df["Smiley"] = df["Confiance"].map(smiley_map)
    return df
def scores_extremes(df_scores): # Récupération des indicateurs les plus favorables/défavorable
    # Pour chaque profil : index du score min et du score max
    idx_min = df_scores.groupby('profil')['score'].idxmin()
    idx_max = df_scores.groupby('profil')['score'].idxmax()
    # Récupération des lignes correspondantes
    df_min = df_scores.loc[idx_min, ['profil', 'indicateur', 'valeur', 'score']]
    df_max = df_scores.loc[idx_max, ['profil', 'indicateur', 'valeur', 'score']]
    df_extremes = (pd.concat([df_max.assign(type='score_max'), df_min.assign(type='score_min')])
                   .sort_values(['profil', 'type'], ascending=[True, False]).reset_index(drop=True))
    return df_extremes

# === FONCTIONS GRAPHIQUES ===
# -- Fonction graphique objectif de cours
def plot_objectif(action_suivie):
    targets = pd.DataFrame(list(action_suivie.analyst_price_targets.items()), columns=['Name','Value'])
    d = targets.set_index('Name')['Value']
    if 'current' in d and 'mean' in d:
        potentiel = (d['mean'] / d['current'] - 1) * 100
    else:
        potentiel = None
    if potentiel>= 0:
        current_color = "#32CD32"
    else:
        current_color = "#FFA500"
    current = targets[targets['Name'].str.lower() == 'current']
    current['0'] = 0.5
    current['Label'] = current.apply(lambda row: f"{row['Name']} : {row['Value']:.2f} €", axis=1)
    targets = targets[targets['Name'].str.lower() != 'current']
    targets['0'] = 0
    targets['Label'] = targets.apply(lambda row: f"{row['Name']} : {row['Value']:.2f} €", axis=1)
    positions = ["top center" if i % 2 == 0 else "bottom center" for i in range(len(targets))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=current['Value'], y=current['0'], mode="markers+text", marker=dict(color=current_color, size=12, symbol="circle"), text=current['Label'],
                             textposition="top center", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=targets['Value'], y=targets['0'], mode="markers+text", marker=dict(color="white", size=12, symbol="circle"), text=targets['Label'],
                             textposition=positions, hoverinfo="skip"))
    fig.update_yaxes(range=[-1, 1])
    fig.update_layout(template="plotly_dark",
                      height=250,
                      margin=dict(l=5, r=5, t=30, b=5),
                      title=f"Objectifs de cours - potentiel = {potentiel:.2f} %",
                      xaxis=dict(showticklabels=False, fixedrange=True),                      
                      yaxis=dict(showticklabels=False, fixedrange=True, showgrid=False),
                      showlegend=False, dragmode=False, hovermode=False)
    fig.update_traces(hoverinfo='skip')
    return fig
# -- Fonction graphique recommandations --
recommendations_colors = {"strongBuy": "#006400", "buy": "#32CD32", "hold": "#808080", "sell": "#FFA500", "strongSell": "#B22222"}
def plot_recommendations(action_suivie):
    types = ["strongBuy", "buy", "hold", "sell", "strongSell"]
    periode_order = ["0m", "-1m", "-2m"]
    recommendations = action_suivie.recommendations
    recommendations = recommendations.set_index("period").loc[periode_order].reset_index()
    df_long = recommendations.melt(id_vars="period", value_vars=types, var_name="type", value_name="count")
    fig = go.Figure()
    for t in types:
        df_t = df_long[df_long["type"] == t]
        fig.add_trace(go.Bar(x=df_t["period"], y=df_t["count"], name=t, marker_color=recommendations_colors[t]))
    fig.update_layout(template="plotly_dark",
                      height=250,
                      margin=dict(l=5, r=5, t=30, b=5),
                      title="Recommandations des analystes (nombre)",
                      barmode="group",
                      yaxis=dict(showticklabels=False, fixedrange=True, showgrid=False),
                      showlegend=False, dragmode=False)
    return fig
# -- Fonction graphique croissance CA --
def plot_revenue(action_suivie):
    df = action_suivie.revenue_estimate
    df = df.loc[["0y", "+1y"]].copy()
    yearAgo = df.loc["0y", "yearAgoRevenue"]
    low_0y  = df.loc["0y", "low"]
    low_1y  = df.loc["+1y", "low"]
    avg_0y  = df.loc["0y", "avg"]
    avg_1y  = df.loc["+1y", "avg"]
    high_0y = df.loc["0y", "high"]
    high_1y = df.loc["+1y", "high"]
    serie_low  = [yearAgo, low_0y,  low_1y]
    serie_avg  = [yearAgo, avg_0y,  avg_1y]
    serie_high = [yearAgo, high_0y, high_1y]
    text_low  = ["", f"{serie_low[1]/1e6:.0f} M",  f"{serie_low[2]/1e6:.0f} M"]
    text_avg  = [f"{serie_avg[0]/1e6:.0f} M", f"{serie_avg[1]/1e6:.0f} M<br>({df.loc["0y", "growth"]*100:.1f} %)", f"{serie_avg[2]/1e6:.0f} M<br>({df.loc["+1y", "growth"]*100:.1f} %)"]
    text_high = ["", f"{serie_high[1]/1e6:.0f} M", f"{serie_high[2]/1e6:.0f} M"]
    index = ["yearAgo", "0y", "+1y"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=index, y=serie_low, mode="lines+markers+text", line=dict(color="#FFA500"), hoverinfo="skip",
                             text=text_low, textposition="bottom center", textfont=dict(color="#FFA500")))
    fig.add_trace(go.Scatter(x=index, y=serie_avg, mode="lines", fill='tonexty', line=dict(color="#FFA500", width=0), hoverinfo="skip",))
    fig.add_trace(go.Scatter(x=index, y=serie_avg, mode="lines+markers+text", line=dict(color="white"), hoverinfo="skip",
                             text=text_avg, textposition="top center"))
    fig.add_trace(go.Scatter(x=index, y=serie_high, mode="lines+text", fill='tonexty', name="High", line=dict(color="#2ca02c"), hoverinfo="skip",
                             text=text_high, textposition="top center", textfont=dict(color="#2ca02c")))
    fig.update_layout(template="plotly_dark",
                      height=300,
                      margin=dict(l=5, r=5, t=30, b=5),
                      title="Perspectives de croissance du CA",
                      xaxis=dict(showticklabels=False),
                      yaxis=dict(showticklabels=False, showgrid=False),
                      showlegend=False, dragmode=False)
    return fig
# -- Fonction graphique EPS --
def plot_EPS(action_suivie):
    df = action_suivie.earnings_estimate
    df = df.loc[["0y", "+1y"]].copy()
    yearAgo = df.loc["0y", "yearAgoEps"]
    low_0y  = df.loc["0y", "low"]
    low_1y  = df.loc["+1y", "low"]
    avg_0y  = df.loc["0y", "avg"]
    avg_1y  = df.loc["+1y", "avg"]
    high_0y = df.loc["0y", "high"]
    high_1y = df.loc["+1y", "high"]
    serie_low  = [yearAgo, low_0y,  low_1y]
    serie_avg  = [yearAgo, avg_0y,  avg_1y]
    serie_high = [yearAgo, high_0y, high_1y]
    text_low  = ["", f"{serie_low[1]:.2f} €",  f"{serie_low[2]:.2f} €"]
    text_avg  = [f"{serie_avg[0]:.2f} €", f"{serie_avg[1]:.2f} €<br>({df.loc["0y", "growth"]*100:.1f} %)", f"{serie_avg[2]:.2f} €<br>({df.loc["+1y", "growth"]*100:.1f} %)"]
    text_high = ["", f"{serie_high[1]:.2f} €", f"{serie_high[2]:.2f} €"]
    index = ["yearAgo", "0y", "+1y"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=index, y=serie_low, mode="lines+markers+text", line=dict(color="#FFA500"), hoverinfo="skip",
                             text=text_low, textposition="bottom center", textfont=dict(color="#FFA500")))
    fig.add_trace(go.Scatter(x=index, y=serie_avg, mode="lines", fill='tonexty', line=dict(color="#FFA500", width=0), hoverinfo="skip",))
    fig.add_trace(go.Scatter(x=index, y=serie_avg, mode="lines+markers+text", line=dict(color="white"), hoverinfo="skip",
                             text=text_avg, textposition="top center"))
    fig.add_trace(go.Scatter(x=index, y=serie_high, mode="lines+text", fill='tonexty', name="High", line=dict(color="#2ca02c"), hoverinfo="skip",
                             text=text_high, textposition="top center", textfont=dict(color="#2ca02c")))
    fig.update_layout(template="plotly_dark",
                      height=300,
                      margin=dict(l=5, r=5, t=30, b=5),
                      title="Prévisions de Bénéfice par action",
                      xaxis=dict(showticklabels=False),
                      yaxis=dict(showticklabels=False, showgrid=False),
                      showlegend=False, dragmode=False)
    return fig
# -- Fonction graphique vue du jour --
def plot_intraday(day_vue, action_suivie):
    x = list(range(len(day_vue)))
    last_price = day_vue["Close"].iloc[-1]
    fig = go.Figure()
    # Courbe des cours
    fig.add_trace(go.Scatter(x=x, y=day_vue["Close"], mode="lines", line=dict(color="white", width=2), name="Cours de clôture",
                             hovertext=day_vue.index.strftime("%H:%M"), hoverinfo="text+y"))
    # Ligne pointillée du dernier cours
    fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[last_price, last_price], mode="lines",
                             line=dict(color="#00FFFF", width=1.5, dash="dash"), name="Dernier cours", hoverinfo=None))
    # Volume en barres (axe secondaire)
    fig.add_trace(go.Bar(x=x, y=day_vue["Volume"], marker_color="gray", name="Volume", yaxis="y2", opacity=0.4,
                         hovertext=day_vue.index.strftime("%H:%M"), hoverinfo="text+y"))
    # Mise en forme
    fig.update_layout(template="plotly_dark",
                      margin=dict(l=5, r=5, t=30, b=5),
                      title=(f"{action_suivie.info['shortName']} - {day_vue.index.max().strftime('%d %b %Y %H:%M')}"),
                      xaxis=dict(tickmode="array", tickvals=x[::60], ticktext=day_vue.index[::60].strftime("%H:%M"), tickangle=45),
                      yaxis=dict(title="Cours (€)"),
                      yaxis2=dict(overlaying="y", side="right", range=[0, day_vue["Volume"].max() * 4], showticklabels=False, showgrid=False),
                      bargap=0,
                      height=500,
                      showlegend=False)
    return fig
# -- Fonction graphique vue année complète --
def plot_1year(year_vue, action_suivie):
    x = list(range(len(year_vue)))
    fig = go.Figure()
    # Cours de cloture
    fig.add_trace(go.Scatter(x=x, y=year_vue["Close"], mode="lines", line=dict(color="white", width=2), name="Cours de clôture",
                             hovertemplate="<b>%{fullData.name}</b><br>"+"Date : %{text}<br>"+"Valeur : %{y:.2f} €<extra></extra>",
                             text=year_vue.index.strftime("%d %b %Y")))
    # Bande High–Low
    fig.add_trace(go.Scatter(x=x, y=year_vue["Low"], mode="lines", fill='tonexty', line=dict(color="white", width=0), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=x, y=year_vue["High"], mode="lines", line=dict(color="white", width=0), hoverinfo="skip", showlegend=False))
    # Moyennes mobiles
    fig.add_trace(go.Scatter(x=x, y=year_vue["MA20"], mode="lines", line=dict(color="orange", width=1), name="MA20",
                             hovertemplate="<b>%{fullData.name}</b><br>"+"Date : %{text}<br>"+"Valeur : %{y:.2f} €<extra></extra>",
                             text=year_vue.index.strftime("%d %b %Y")))
    fig.add_trace(go.Scatter(x=x, y=year_vue["MA50"], mode="lines", line=dict(color="cyan", width=1), name="MA50",
                             hovertemplate="<b>%{fullData.name}</b><br>"+"Date : %{text}<br>"+"Valeur : %{y:.2f} €<extra></extra>",
                             text=year_vue.index.strftime("%d %b %Y")))
    # Support / résistance simples
    fig.add_trace(go.Scatter(x=x, y=year_vue["support"], mode="lines", line=dict(color="white", width=1, dash="dash"), name="Support", showlegend=False,
                             hovertemplate="<b>%{fullData.name}</b><br>"+"Date : %{text}<br>"+"Valeur : %{y:.2f} €<extra></extra>",
                             text=year_vue.index.strftime("%d %b %Y")))
    fig.add_trace(go.Scatter(x=x, y=year_vue["resistance"], mode="lines", line=dict(color="white", width=1, dash="dash"), name="Resistance", showlegend=False,
                             hovertemplate="<b>%{fullData.name}</b><br>"+"Date : %{text}<br>"+"Valeur : %{y:.2f} €<extra></extra>",
                             text=year_vue.index.strftime("%d %b %Y")))
    # Volume en barres (axe secondaire)
    fig.add_trace(go.Bar(x=x, y=year_vue["Volume"], marker_color="gray", name="Volume", yaxis="y2", opacity=0.4,
                         hovertext=year_vue.index.strftime("%d %b %Y"), hoverinfo="text+y"))
    # Dividendes en sur-graphe
    div_non_nuls = year_vue[year_vue["Dividends"] > 0]
    div_non_nuls = div_non_nuls.copy()
    div_non_nuls['DivExist'] = 1
    fig.add_trace(go.Scatter(x=div_non_nuls.index.map(lambda d: year_vue.index.get_loc(d)), y=div_non_nuls["DivExist"], customdata=div_non_nuls["Dividends"],
                             mode="markers", marker=dict(color="white", size=10, symbol="diamond"), name="Dividende", yaxis="y3", showlegend=False,
                             hovertemplate="<b>%{fullData.name}</b><br>"+"Date : %{text}<br>"+"Dividende : %{customdata:.2f} €<extra></extra>",
                             text=div_non_nuls.index.strftime("%d %b %Y")))
    fig.data = fig.data[::-1]
    # Mise en forme
    fig.update_layout(template="plotly_dark",
                      margin=dict(l=5, r=5, t=30, b=5),
                      title=(f"{action_suivie.info['shortName']} - du {year_vue.index.min().date().strftime("%d %b %Y")} au {year_vue.index.max().date().strftime("%d %b %Y")}"),
                      xaxis=dict(tickmode="array", tickvals=x[::60], ticktext=year_vue.index[::60].strftime("%b %Y")),
                      yaxis=dict(title="Cours (€)", showgrid=True),
                      yaxis2=dict(overlaying="y", side="right", range=[0, year_vue["Volume"].max() * 4], showticklabels=False, showgrid=False),
                      yaxis3=dict(overlaying="y", side="right", range=[0, 1.05], showticklabels=False, showgrid=False),
                      legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="left", x=0),
                      bargap=0,
                      height=600)
    return fig
# -- Fonction de définition des couleurs pour les recommandations
def color_reco(val):
    return f"background-color: {recommendations_colors.get(val, 'white')};"
# -- Fonction graphique scores catégories --
def plot_categories(score_categories):
    fig = go.Figure()
    for t in score_categories['categorie'].unique():
        valeur = 0.5 - score_categories.loc[score_categories['categorie'] == t, 'score_categorie'].values[0]
        color = "green" if valeur > 0 else "red"
        fig.add_trace(go.Bar(x=[t], y=[valeur], name=t, marker_color=color))
    fig.add_hline(y=0, line_color="white", line_width=2)
    fig.update_layout(template="plotly_dark",
                      height=250,
                      margin=dict(l=5, r=5, t=30, b=5),
                      barmode="group",
                      yaxis=dict(range=[-0.5, 0.5], showticklabels=False, fixedrange=True, showgrid=False),
                      showlegend=False, dragmode=False)
    return fig
# -- Fonction d'affichage des métrics extremes
def afficher_extreme(indicateur, valeur, type_score):
    if type_score == "score_min":
        icon = "🟢"   # bulle verte
    else:
        icon = "🔴"   # bulle rouge
    st.metric(label=f"{icon} {indicateur}", value=valeur, format="percent")

# === APPLICATION ===
st.set_page_config(layout="wide")
tickers_paris = charger_tickers_euronext_paris()
# -- Sidebar pour le choix de l'action à analyser --
with st.sidebar:
    st.title("Euronext Paris", width="stretch", text_alignment="left")
    st.header("Choix du titre à analyser")
    select_ticker = st.dataframe(tickers_paris[['Name', 'ISIN', 'Symbol']],
                                 width="content", hide_index=True,
                                 on_select="rerun", selection_mode="single-row")
selected_ticker = tickers_paris.iloc[select_ticker.selection['rows']]
# -- Affichage des résultats --
if len(select_ticker.selection['rows']) == 0:
    st.header("Choisir le titre à afficher dans la liste sur le côté")
else:
    ticker = selected_ticker['Ticker'].iloc[0]
    try:
        # -- Chargement des données yfinance --
        data = charge_donnees_bourse(ticker)
        # -- Calcul des scores de performance
        df_scores = df_seuils.copy()
        df_scores['valeur'] = df_scores.apply(lambda row: safe_get_value(data.indicateurs, row["indicateur"]), axis=1)
        df_scores['score'] = df_scores.apply(lambda row: score(row['valeur'], row['obj_min'], row['obj_max'], row['cat_min'], row['cat_max']), axis=1)
        df_scores_categories = score_categorie(df_scores, df_poids)
        df_score_global = score_global(df_scores_categories, df_poids)
        df_extremes = scores_extremes(df_scores)
        # -- Header --
        st.title(f"{data.action_suivie.info['longName']}")
        st.write(f"ISIN: {data.action_suivie.isin} | Symbole: {data.action_suivie.info['symbol']}")
        # -- corps --
        with st.container():
            # -- Partie haute : Affichage données financières et cours du jour
            with st.container(height=620):
                col1, col2 = st.columns([0.6, 0.4], gap="small", border=True)
                # -- Colonne de gauche : Onglets de présentation des données et analyses financières
                tab1, tab2, tab3, tab4 = col1.tabs(["Indicateurs financiers", "Recommandations", "Informations société", "Définitions"])
                # -- Indicateurs financiers
                with tab1.container(gap="xsmall", border=False, width="stretch", height=500):
                    # -- Indicateurs monétaires
                    with st.container(horizontal=True, border=True, width="stretch"):
                        m1, m2, m3, m4 = st.columns(4, width="stretch")
                        actual = f"{data.day_vue["Close"].iloc[-1]:.{2 if data.day_vue["Close"].iloc[-1] >= 10 else 4}f} €"
                        evol = data.day_vue["Close"].iloc[-1] / data.day_vue["Close"].iloc[0] - 1
                        m1.metric("Cours actuel", actual, evol, format="percent")                            
                        m2.metric('Cours moyen / 1 an', data.indicateurs['Cours moyen / 1 an'], f"{data.indicateurs['Delta cours moyen'].iloc[0] * 100:.2f} %", format="euro")
                        m3.metric('MA50', data.indicateurs['MA50'], f"{data.indicateurs['Delta MA50'].iloc[0] * 100:.2f} %", format="euro")
                        m4.metric('ATH / 1 an', data.indicateurs['ATH / 1 an'], f"{data.indicateurs['Delta ATH'].iloc[0] * 100:.2f} %", format="euro")
                    # -- Dividendes et ratios
                    with st.container(horizontal=True, border=True, width="stretch"):
                        d1, r1, r2, r3 = st.columns(4, width="stretch")
                        d1.metric('Dividendes', data.indicateurs['Dividendes'], format="euro")
                        r1.metric('Div %', f"{data.indicateurs['Div %'].iloc[0] * 100:.2f} %", icon=data.risque['Div %'].iloc[0])
                        r2.metric('Rendement', f"{data.indicateurs['Rendement'].iloc[0] * 100:.2f} %", icon=data.risque['Rendement'].iloc[0])
                        r3.metric('Volatilité', f"{data.indicateurs['Volatilité'].iloc[0] * 100:.2f} %", icon=data.risque['Volatilité'].iloc[0])
                    # -- Objectifs et recommandations
                    with st.container(horizontal=True, border=True, width="stretch"):
                        obj, reco = st.columns(2, width="stretch")
                        try:
                            fig_obj = plot_objectif(data.action_suivie)
                            obj.plotly_chart(fig_obj, width="stretch", height=200, config={"displayModeBar": False})
                        except:
                            obj.write("**Objectifs de cours**")
                            obj.write("Données indisponibles")
                        try:
                            fig_reco = plot_recommendations(data.action_suivie)
                            reco.plotly_chart(fig_reco, width="stretch", height=200, config={"displayModeBar": False})
                        except:
                            reco.write("**Recommandations des analystes**")
                            reco.write("Données indisponibles")
                # -- Recommandation calculée
                with tab2.container(gap="xxsmall", border=False, width="stretch", height=500):
                    df_column_config = {'Recommandation': st.column_config.TextColumn("Recommandation", alignment="center"),
                                        'Smiley': st.column_config.TextColumn("", alignment="center")}
                    col_reco1, col_reco2, col_reco3 = st.columns(3, gap="xsmall", border=True)
                    # -- Recommandation Profil Prudent
                    with col_reco1:
                        try:
                            df_reco = df_score_global[['Recommandation','Smiley']].loc[df_score_global['profil'] == 'prudent']
                            df_reco = df_reco.style.map(color_reco, subset=['Recommandation'])
                            df_cat = df_scores_categories[['categorie','score_categorie']].loc[df_scores_categories['profil'] == 'prudent']
                            fig_cat = plot_categories(df_cat)
                            st.markdown("🛡️ **Profil Prudent**")
                            st.dataframe(df_reco, column_config = df_column_config, width="stretch", hide_index=True)
                            st.plotly_chart(fig_cat, width="stretch", height=140, config={"displayModeBar": False})
                            df_p = df_extremes[df_extremes['profil'] == 'prudent']
                            for _, row in df_p.iterrows():
                                afficher_extreme(indicateur=row['indicateur'], valeur=row['valeur'], type_score=row['type'])
                        except:
                            st.markdown("🛡️ **Profil Prudent**")
                            st.write("Recommandations indisponibles")
                    # -- Recommandation Profil Equilibré
                    with col_reco2:
                        try:
                            df_reco = df_score_global[['Recommandation','Smiley']].loc[df_score_global['profil'] == 'équilibré']
                            df_reco = df_reco.style.map(color_reco, subset=['Recommandation'])
                            df_cat = df_scores_categories[['categorie','score_categorie']].loc[df_scores_categories['profil'] == 'équilibré']
                            fig_cat = plot_categories(df_cat)
                            st.markdown("⚖️ **Profil Equilibré**")
                            st.dataframe(df_reco, column_config = df_column_config, width="stretch", hide_index=True)
                            st.plotly_chart(fig_cat, width="stretch", height=140, config={"displayModeBar": False})
                            df_p = df_extremes[df_extremes['profil'] == 'équilibré']
                            for _, row in df_p.iterrows():
                                afficher_extreme(indicateur=row['indicateur'], valeur=row['valeur'], type_score=row['type'])
                        except:
                            st.markdown("⚖️ **Profil Equilibré**")
                            st.write("Recommandations indisponibles")
                    # -- Recommandation Profil Dynamique
                    with col_reco3:
                        try:
                            df_reco = df_score_global[['Recommandation','Smiley']].loc[df_score_global['profil'] == 'dynamique']
                            df_reco = df_reco.style.map(color_reco, subset=['Recommandation'])
                            df_cat = df_scores_categories[['categorie','score_categorie']].loc[df_scores_categories['profil'] == 'dynamique']
                            fig_cat = plot_categories(df_cat)
                            st.markdown("🚀 **Profil Dynamique**")
                            st.dataframe(df_reco, column_config = df_column_config, width="stretch", hide_index=True)
                            st.plotly_chart(fig_cat, width="stretch", height=140, config={"displayModeBar": False})
                            df_p = df_extremes[df_extremes['profil'] == 'dynamique']
                            for _, row in df_p.iterrows():
                                afficher_extreme(indicateur=row['indicateur'], valeur=row['valeur'], type_score=row['type'])
                        except:
                            st.markdown("🚀 **Profil Dynamique**")
                            st.write("Recommandations indisponibles")
                # -- Informations sur la société
                with tab3.container(gap="xxsmall", border=False, width="stretch", height=500):
                    col_info1, col_info2 = st.columns(2, gap="small", border=True)
                    # -- Informations générales
                    with col_info1.container(border=False, width="stretch", height=460):
                        try:
                            st.subheader(data.action_suivie.info['sectorDisp'])
                        except:
                            st.write("Secteur inconnu")
                        try:
                            st.write(data.action_suivie.info['longBusinessSummary'])
                        except:
                            st.write("Informations indisponibles")
                    # -- Perspectives CA et EPS
                    try:
                        fig_rev = plot_revenue(data.action_suivie)
                        col_info2.plotly_chart(fig_rev, width="stretch", height=200, config={"displayModeBar": False})
                    except:
                        col_info2.write("**Perspectives de croissance du CA**")
                        col_info2.write("Données indisponibles")
                    try:
                        fig_eps = plot_EPS(data.action_suivie)
                        col_info2.plotly_chart(fig_eps, width="stretch", height=200, config={"displayModeBar": False})
                    except:
                        col_info2.write("**Prévisions de Bénéfice par action**")
                        col_info2.write("Données indisponibles")
                # -- Définitions des ratios
                with tab4.container(gap="xxsmall", border=False, width="stretch", height=500):
                    row1 = st.container(border=True, width="stretch")
                    row1.markdown(":moneybag: **Div %** = dividendes / cours moyen sur 1 an")
                    row1.write("Mesure directe des bénéfices pour l'investisseur par rapport au montant investi. Un ratio faible (<2%) correspond à une entreprise qui réinvestit ses profits. Un ratio moyen (2 à 5%) correspond à une entreprise mature qui équilibre croissance et distribution. Un ratio élevé (>6%) est attractif mais dangereux.")
                    row2 = st.container(border=True, width="stretch")
                    row2.markdown(":moneybag: **Rendement** = évolution du cours de l'action sur 1 an")
                    row2.write("Il reflète l'évaluation de l'entreprise par le marché en fonction de ces résultats (croissance, marges, dette) passés et à venir. Un rendement faible (<5%) indique une sous-performance ou un risque perçu. Un rendement moyen (5 à 15%) indique une perception équilibrée, neutre. Un rendement élevé (>15%) indique la présence d'un catalyseur et un fort niveau de confiance.")
                    row3 = st.container(border=True, width="stretch")
                    row3.markdown(":moneybag: **Volatilité** = écart-type des variations de prix")
                    row3.write("La volatilité est un indicateur direct du risque qui traduit l'incertitude et la sensibilité aux événements. Une volatilité faible (<15%) indique un actif stable et prévisible. Une volatilité moyenne (15 à 30%) correspond à un actif normal. Une volatilité élevée (>30%) indique une entreprise cyclique ou en transformation et un sentiment de marché instable")
                # -- Colonne de droite : Graphique du cours du jour
                try:
                    fig_day = plot_intraday(data.day_vue, data.action_suivie)
                    col2.plotly_chart(fig_day, width=500, height="content")
                except:
                    col2.write("**Evolution du cours du jour**")
                    col2.write("Données indisponibles")
            # -- Partie basse : Graphique de l'évolution à 12 mois
            with st.container(border=True, height=600):
                try:
                    fig_year = plot_1year(data.year_vue, data.action_suivie)
                    st.plotly_chart(fig_year, width="stretch", height="stretch")
                except:
                    st.write("**Evolution du cours sur 12 mois**")
                    st.write("Données indisponibles")
    except:
        st.header(f"Données financières indisponibles pour {selected_ticker['Ticker'].iloc[0]} - {selected_ticker['Name'].iloc[0]}")
