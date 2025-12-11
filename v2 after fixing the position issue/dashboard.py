import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="Équipe Nationale du Maroc 🇲🇦",
    page_icon="⚽",
    layout="wide"
)

# Fonction pour nettoyer les valeurs de marché
def clean_market_value(value):
    if pd.isna(value) or value == "N/A" or value == "-":
        return 0
    
    value = str(value).strip()
    multiplier = 1
    
    if "mio" in value.lower() or "m" in value.lower():
        multiplier = 1_000_000
    elif "k" in value.lower():
        multiplier = 1_000
    
    number = ''.join(c for c in value if c.isdigit() or c == ',' or c == '.')
    number = number.replace(',', '.')
    
    try:
        return float(number) * multiplier
    except:
        return 0

# Charger les données
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("equipe_maroc.csv")
        df['market_value_numeric'] = df['market_value'].apply(clean_market_value)
        df['age_numeric'] = pd.to_numeric(df['age'], errors='coerce')
        # Convert goals and assists to numeric, handling 'N/A'
        df['goals_numeric'] = pd.to_numeric(df['goals'], errors='coerce').fillna(0)
        df['assists_numeric'] = pd.to_numeric(df['assists'], errors='coerce').fillna(0)
        return df
    except FileNotFoundError:
        st.error("❌ Fichier 'equipe_maroc.csv' non trouvé. Exécute d'abord le script de scraping (l.py).")
        st.stop()
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        st.stop()

df = load_data()

# Titre principal
st.title("⚽ Dashboard - Équipe Nationale du Maroc 🇲🇦")
st.markdown("---")

# Sidebar — filtre âge uniquement
st.sidebar.header("🔍 Filtres")

age_range = st.sidebar.slider(
    "Tranche d'âge",
    int(df['age_numeric'].min()) if not df['age_numeric'].isna().all() else 18,
    int(df['age_numeric'].max()) if not df['age_numeric'].isna().all() else 40,
    (18, 40)
)

# Filtrer les données
df_filtered = df[
    (df['age_numeric'] >= age_range[0]) &
    (df['age_numeric'] <= age_range[1])
]

# Métriques clés
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Nombre de joueurs", len(df_filtered))

with col2:
    avg_age = df_filtered['age_numeric'].mean()
    st.metric("📅 Âge moyen", f"{avg_age:.1f} ans" if not pd.isna(avg_age) else "N/A")

with col3:
    total_value = df_filtered['market_value_numeric'].sum() / 1_000_000
    st.metric("💰 Valeur totale", f"{total_value:.1f}M €")

with col4:
    avg_value = df_filtered['market_value_numeric'].mean() / 1_000_000
    st.metric("📊 Valeur moyenne", f"{avg_value:.2f}M €" if not pd.isna(avg_value) else "N/A")

st.markdown("---")

# Métriques de performance
col5, col6, col7 = st.columns(3)

with col5:
    total_goals = df_filtered['goals_numeric'].sum()
    st.metric("⚽ Buts totaux", int(total_goals) if total_goals > 0 else "N/A")

with col6:
    total_assists = df_filtered['assists_numeric'].sum()
    st.metric("🎯 Passes décisives", int(total_assists) if total_assists > 0 else "N/A")

with col7:
    goals_per_player = df_filtered['goals_numeric'].mean()
    st.metric("⚽ Buts/joueur", f"{goals_per_player:.2f}" if goals_per_player > 0 else "N/A")

st.markdown("---")

# Graphiques
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Distribution des âges")
    fig2 = px.histogram(
        df_filtered,
        x='age_numeric',
        nbins=15,
        color_discrete_sequence=['#C1272D']
    )
    fig2.update_layout(
        xaxis_title="Âge",
        yaxis_title="Nombre de joueurs",
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("💎 Top 10 - Valeur marchande")
    fig3 = px.bar(
        df_filtered.nlargest(10, 'market_value_numeric'),
        x='market_value_numeric',
        y='name',
        orientation='h',
        color='market_value_numeric',
        color_continuous_scale='Reds',
        labels={'market_value_numeric': 'Valeur (€)', 'name': 'Joueur'}
    )
    fig3.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig3, use_container_width=True)

# Relation âge vs valeur marchande
st.subheader("🔄 Âge vs Valeur marchande")
fig4 = px.scatter(
    df_filtered[df_filtered['market_value_numeric'] > 0],
    x='age_numeric',
    y='market_value_numeric',
    size='market_value_numeric',
    hover_data=['name', 'market_value'],
    color_discrete_sequence=['#C1272D'],
    labels={
        'age_numeric': 'Âge',
        'market_value_numeric': 'Valeur marchande (€)'
    }
)
fig4.update_layout(height=400)
st.plotly_chart(fig4, use_container_width=True)

# Tableau final avec toutes les données
st.subheader("📋 Données complètes")
display_columns = ['name', 'age', 'position', 'market_value', 'goals', 'assists', 'time_played']
available_columns = [col for col in display_columns if col in df_filtered.columns]
st.dataframe(
    df_filtered[available_columns].sort_values('name'),
    use_container_width=True,
    hide_index=True
)

# Télécharger les données
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Télécharger les données filtrées (CSV)",
    data=csv,
    file_name="equipe_maroc.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Données extraites de Transfermarkt | Dashboard créé avec Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
