import json
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# -------------------------- Page Config & Style --------------------------
st.set_page_config(page_title="STAG vs PROD Showdown", layout="wide")
st.title("🔥 STAG vs PROD: Expired URLs Battle Arena 🔥")

# Custom CSS for some sugar
st.markdown("""
<style>
    .big-font { font-size: 24px !important; font-weight: bold; }
    .diff-good { color: #00ff00; background-color: #002b00; padding: 5px; border-radius: 5px; }
    .diff-bad { color: #ff3333; background-color: #330000; padding: 5px; border-radius: 5px; }
    .diff-neutral { color: #ffff00; background-color: #333300; padding: 5px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)


# -------------------------- Load Data --------------------------
@st.cache_data
def load_env_data(file_path, env_name):
    with open(file_path) as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['videoURL'] = df['videoURLs'].apply(lambda x: x[0]['videoURL'] if x else None)
    df['expired'] = pd.to_datetime(df['expired'])
    df['year'] = df['expired'].dt.year
    df['env'] = env_name
    return df


try:
    df_stag = load_env_data('mtcms-stag-response.json', 'Staging')
    df_prod = load_env_data('mtcms-prod-response.json', 'Production')
except FileNotFoundError as e:
    st.error(f"Missing file: {e}")
    st.stop()

# Combine both
df_combined = pd.concat([df_stag, df_prod], ignore_index=True)

# -------------------------- Metrics & Badges --------------------------
col1, col2, col3, col4 = st.columns(4)

total_stag = len(df_stag)
total_prod = len(df_prod)
diff_count = total_stag - total_prod
diff_pct = (diff_count / total_prod * 100) if total_prod > 0 else 0

with col1:
    st.metric("Staging Expired", total_stag, delta=None)
with col2:
    st.metric("Production Expired", total_prod, delta=f"{diff_count:+} vs STAG")
with col3:
    if diff_pct > 10:
        st.markdown(f"<span class='diff-bad big-font'>+{diff_pct:.1f}% more than PROD</span>", unsafe_allow_html=True)
    elif diff_pct < -10:
        st.markdown(f"<span class='diff-good big-font'>{diff_pct:.1f}% fewer than PROD</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span class='diff-neutral big-font'>{diff_pct:.1f}% diff</span>", unsafe_allow_html=True)
with col4:
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%b %d, %Y %H:%M')}")

st.markdown("---")

# -------------------------- Interactive Comparison --------------------------
tab1, tab2, tab3 = st.tabs(["Yearly Comparison", "Side-by-Side Drilldown", "Diff Detective"])

with tab1:
    st.subheader("Expired URLs per Year – Who’s Worse?")

    yearly = df_combined.groupby(['year', 'env']).size().reset_index(name='count')

    fig = px.bar(yearly, x='year', y='count', color='env',
                 barmode='group',
                 text='count',
                 color_discrete_map={'Staging': '#FF6B6B', 'Production': '#4ECDC4'},
                 labels={'count': 'Expired URLs', 'year': 'Year'},
                 title="STAG vs PROD: Expired URLs Over Time")
    fig.update_traces(textposition='outside')
    fig.update_layout(legend_title="Environment")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Drill Down by Year")
    selected_year = st.selectbox("Choose Year", sorted(df_combined['year'].unique()), key="drilldown")

    col_a, col_b = st.columns(2)

    stag_year = df_stag[df_stag['year'] == selected_year][['mappedOfferId', 'videoURL', 'expired']]
    prod_year = df_prod[df_prod['year'] == selected_year][['mappedOfferId', 'videoURL', 'expired']]

    with col_a:
        st.markdown("**Staging**")
        st.dataframe(stag_year, use_container_width=True, height=400)
        st.caption(f"{len(stag_year)} expired URLs")

    with col_b:
        st.markdown("**Production**")
        st.dataframe(prod_year, use_container_width=True, height=400)
        st.caption(f"{len(prod_year)} expired URLs")

with tab3:
    st.subheader("Diff Detective – What’s in STAG but NOT in PROD?")

    # Find URLs only in staging
    stag_only = df_stag[~df_stag['videoURL'].isin(df_prod['videoURL'])]
    prod_only = df_prod[~df_prod['videoURL'].isin(df_stag['videoURL'])]

    colx, coly = st.columns(2)

    with colx:
        st.markdown("**Only in Staging** (Potential false positives?)")
        if len(stag_only) > 0:
            st.dataframe(stag_only[['mappedOfferId', 'videoURL', 'expired']], use_container_width=True)
            st.error(f"{len(stag_only)} URLs expired in STAG but still alive in PROD?")
        else:
            st.success("Nothing! STAG is clean")

    with coly:
        st.markdown("**Only in Production** (Oh no!)")
        if len(prod_only) > 0:
            st.dataframe(prod_only[['mappedOfferId', 'videoURL', 'expired']], use_container_width=True)
            st.warning(f"{len(prod_only)} URLs expired in PROD but not in STAG – data drift?")
        else:
            st.success("All good!")

# -------------------------- Fun Footer --------------------------
st.markdown("---")
st.caption("Made with ☕ + Streamlit + Plotly | Keep your environments in sync!")
