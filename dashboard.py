import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Morocco National Team Dashboard",
    page_icon="🇲🇦",
    layout="wide"
)

# Title and description
st.title("🇲🇦 Morocco National Team Dashboard")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("equipe_maroc.csv")
        
        # Clean market value column
        df['market_value_numeric'] = df['market_value'].replace('-', '0')
        df['market_value_numeric'] = df['market_value_numeric'].str.replace('€', '')
        df['market_value_numeric'] = df['market_value_numeric'].str.replace('m', '000000')
        df['market_value_numeric'] = df['market_value_numeric'].str.replace('k', '000')
        df['market_value_numeric'] = pd.to_numeric(df['market_value_numeric'], errors='coerce')
        
        # Extract age as number
        df['age_numeric'] = df['age'].str.extract(r'\((\d+)\)')[0]
        df['age_numeric'] = pd.to_numeric(df['age_numeric'], errors='coerce')
        
        # Clean height
        df['height_numeric'] = df['height'].str.extract(r'(\d+[,\.]\d+)')[0]
        df['height_numeric'] = df['height_numeric'].str.replace(',', '.')
        df['height_numeric'] = pd.to_numeric(df['height_numeric'], errors='coerce')
        
        return df
    except FileNotFoundError:
        st.error("❌ File 'equipe_maroc.csv' not found! Please run the scraper first.")
        return None

df = load_data()

if df is not None:
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Position filter
    positions = ['All'] + sorted(df['position'].dropna().unique().tolist())
    selected_position = st.sidebar.selectbox("Position", positions)
    
    # Age filter
    if df['age_numeric'].notna().any():
        min_age = int(df['age_numeric'].min())
        max_age = int(df['age_numeric'].max())
        age_range = st.sidebar.slider("Age Range", min_age, max_age, (min_age, max_age))
    
    # Foot filter
    feet = ['All'] + sorted(df['foot'].dropna().unique().tolist())
    selected_foot = st.sidebar.selectbox("Preferred Foot", feet)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_position != 'All':
        filtered_df = filtered_df[filtered_df['position'] == selected_position]
    if df['age_numeric'].notna().any():
        filtered_df = filtered_df[
            (filtered_df['age_numeric'] >= age_range[0]) & 
            (filtered_df['age_numeric'] <= age_range[1])
        ]
    if selected_foot != 'All':
        filtered_df = filtered_df[filtered_df['foot'] == selected_foot]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", len(filtered_df))
    
    with col2:
        avg_age = filtered_df['age_numeric'].mean()
        st.metric("Average Age", f"{avg_age:.1f}" if not pd.isna(avg_age) else "N/A")
    
    with col3:
        total_value = filtered_df['market_value_numeric'].sum() / 1_000_000
        st.metric("Total Market Value", f"€{total_value:.1f}M")
    
    with col4:
        avg_height = filtered_df['height_numeric'].mean()
        st.metric("Average Height", f"{avg_height:.2f}m" if not pd.isna(avg_height) else "N/A")
    
    st.markdown("---")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💰 Market Value", "📏 Physical Stats", "📋 Data Table"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Position distribution
            st.subheader("Players by Position")
            position_counts = filtered_df['position'].value_counts()
            fig_position = px.pie(
                values=position_counts.values,
                names=position_counts.index,
                title="Position Distribution",
                hole=0.4
            )
            st.plotly_chart(fig_position, use_container_width=True)
        
        with col2:
            # Foot preference
            st.subheader("Preferred Foot Distribution")
            foot_counts = filtered_df['foot'].value_counts()
            fig_foot = px.bar(
                x=foot_counts.index,
                y=foot_counts.values,
                labels={'x': 'Foot', 'y': 'Number of Players'},
                title="Foot Preference",
                color=foot_counts.index
            )
            st.plotly_chart(fig_foot, use_container_width=True)
        
        # Age distribution
        st.subheader("Age Distribution")
        fig_age = px.histogram(
            filtered_df,
            x='age_numeric',
            nbins=15,
            labels={'age_numeric': 'Age', 'count': 'Number of Players'},
            title="Player Age Distribution"
        )
        st.plotly_chart(fig_age, use_container_width=True)
    
    with tab2:
        st.subheader("Market Value Analysis")
        
        # Top 10 most valuable players
        top_10 = filtered_df.nlargest(10, 'market_value_numeric')[
    ['name', 'market_value', 'market_value_numeric', 'position', 'age']
]

        
        fig_top10 = px.bar(
            top_10,
            x='market_value_numeric',
            y='name',
            orientation='h',
            labels={'market_value_numeric': 'Market Value (€)', 'name': 'Player'},
            title="Top 10 Most Valuable Players",
            text='market_value',
            color='market_value_numeric',
            color_continuous_scale='Viridis'
        )
        fig_top10.update_traces(textposition='outside')
        st.plotly_chart(fig_top10, use_container_width=True)
        
        # Market value by position
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Market Value by Position")
            value_by_position = filtered_df.groupby('position')['market_value_numeric'].sum().sort_values(ascending=False)
            fig_position_value = px.bar(
                x=value_by_position.index,
                y=value_by_position.values / 1_000_000,
                labels={'x': 'Position', 'y': 'Total Value (€M)'},
                title="Total Market Value by Position"
            )
            st.plotly_chart(fig_position_value, use_container_width=True)
        
        with col2:
            st.subheader("Average Value by Position")
            avg_value_by_position = filtered_df.groupby('position')['market_value_numeric'].mean().sort_values(ascending=False)
            fig_avg_position_value = px.bar(
                x=avg_value_by_position.index,
                y=avg_value_by_position.values / 1_000_000,
                labels={'x': 'Position', 'y': 'Average Value (€M)'},
                title="Average Market Value by Position",
                color=avg_value_by_position.values
            )
            st.plotly_chart(fig_avg_position_value, use_container_width=True)
    
    with tab3:
        st.subheader("Physical Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Height distribution
            st.subheader("Height Distribution")
            fig_height = px.box(
                filtered_df,
                y='height_numeric',
                x='position',
                labels={'height_numeric': 'Height (m)', 'position': 'Position'},
                title="Height by Position"
            )
            st.plotly_chart(fig_height, use_container_width=True)
        
        with col2:
            # Age vs Market Value scatter
            st.subheader("Age vs Market Value")
            fig_scatter = px.scatter(
                filtered_df,
                x='age_numeric',
                y='market_value_numeric',
                size='market_value_numeric',
                color='position',
                hover_data=['name', 'market_value'],
                labels={
                    'age_numeric': 'Age',
                    'market_value_numeric': 'Market Value (€)'
                },
                title="Age vs Market Value"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Height vs Age scatter
        st.subheader("Height vs Age Analysis")
        fig_height_age = px.scatter(
            filtered_df[filtered_df['height_numeric'].notna()],
            x='age_numeric',
            y='height_numeric',
            color='position',
            hover_data=['name', 'height', 'foot'],
            labels={
                'age_numeric': 'Age',
                'height_numeric': 'Height (m)'
            },
            title="Height vs Age by Position"
        )
        st.plotly_chart(fig_height_age, use_container_width=True)
    
    with tab4:
        st.subheader("Complete Player Data")
        
        # Search functionality
        search_term = st.text_input("🔍 Search player by name", "")
        
        display_df = filtered_df.copy()
        if search_term:
            display_df = display_df[display_df['name'].str.contains(search_term, case=False, na=False)]
        
        # Select columns to display
        columns_to_show = st.multiselect(
            "Select columns to display",
            options=df.columns.tolist(),
            default=['name', 'age', 'position', 'height', 'foot', 'market_value']
        )
        
        st.dataframe(
            display_df[columns_to_show],
            use_container_width=True,
            height=500
        )
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download filtered data as CSV",
            data=csv,
            file_name="morocco_team_filtered.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("**Data Source:** Transfermarkt | **Dashboard created with Streamlit**")

else:
    st.info("👆 Please run the scraper first to generate 'equipe_maroc.csv' file.")