# app.py — FINAL VERSION: Filters + Modal + Deep Diff + Deploy Ready
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor
import time

# ========================= CONFIG =========================
st.set_page_config(
    page_title="STAG vs PROD – Expired URLs Monitor",
    page_icon="Magnifying glass",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========================= STYLING =========================
st.markdown("""
<style>
    .big-font {font-size: 28px !important; font-weight: bold;}
    .metric-good {color: #00aa00; background: #e6ffe6; padding: 10px; border-radius: 10px;}
    .metric-bad  {color: #aa0000; background: #ffe6e6; padding: 10px; border-radius: 10px;}
    .footer {text-align: center; color: #888; margin-top: 4rem;}
    .stDataFrame {font-size: 14px;}
    .modal-table tr:hover {background-color: #f0f8ff;}
</style>
""", unsafe_allow_html=True)


# ========================= DATA LOADER =========================
@st.cache_data(ttl=1800)
def load_data(file_path: str, env_name: str) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        st.warning(f"Generating mock data for {env_name}...")
        mock = [
            {"mappedOfferId": f"{env_name[0]}{i:05d}",
             "videoURLs": [{"videoURL": f"https://{env_name.lower()}.cdn.com/v{i}.mp4"}],
             "expired": f"2024-{'%02d' % ((i % 12) + 1)}-{'%02d' % ((i % 30) + 1)}T00:00:00Z"}
            for i in range(1, 450 if env_name == "Staging" else 380)
        ]
        path.write_text(json.dumps(mock))

    df = pd.DataFrame(json.load(open(path)))
    df["videoURL"] = df["videoURLs"].apply(lambda x: x[0]["videoURL"] if x else None)
    df["expired"] = pd.to_datetime(df["expired"])
    df["year"] = df["expired"].dt.year
    df["month_year"] = df["expired"].dt.strftime("%Y-%m")
    df["date"] = df["expired"].dt.date
    df["env"] = env_name
    return df.drop(columns=["videoURLs"], errors="ignore")


# ========================= MAIN =========================
def main():
    st.title("STAG vs PROD – Expired URLs Deep Monitor")

    stag = load_data("mtcms-stag-response.json", "Staging")
    prod = load_data("mtcms-prod-response.json", "Production")
    combined = pd.concat([stag, prod], ignore_index=True)

    # Header
    diff = len(stag) - len(prod)
    pct = diff / len(prod) * 100 if len(prod) > 0 else 0
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Staging", f"{len(stag):,}")
    with c2:
        st.metric("Production", f"{len(prod):,}", delta=f"{diff:+,}")
    with c3:
        cls = "metric-bad" if diff > 0 else "metric-good"
        st.markdown(f"<div class='{cls} big-font'>{pct:+.1f}%</div>", unsafe_allow_html=True)
    with c4:
        st.caption(f"Updated: {datetime.now():%b %d, %Y %H:%M}")

    st.markdown("---")

    # Global Year Filter
    years = sorted(combined["year"].unique(), reverse=True)
    selected_year = st.selectbox("Focus Year", years, index=0, key="year_filter")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Drilldown + Filters", "Deep Diff", "URL Health"])

    # === TAB 1: Overview ===
    with tab1:
        col1, col2 = st.columns([3, 2])
        with col1:
            fig = px.bar(combined.groupby(["year", "env"], as_index=False).size(),
                         x="year", y="size", color="env", barmode="group")
            st.plotly_chart(fig, width='stretch')
        with col2:
            monthly = combined[combined["year"] == selected_year].groupby(["month_year", "env"], as_index=False).size()
            fig2 = px.line(monthly, x="month_year", y="size", color="env", markers=True)
            st.plotly_chart(fig2, width='stretch')

    # === TAB 2: DRILLDOWN WITH FILTERS + MODAL ===
    with tab2:
        st.subheader(f"All Expired URLs in {selected_year}")

        # Filters
        colf1, colf2, colf3, colf4 = st.columns(4)
        with colf1:
            env_filter = st.multiselect("Environment", ["Staging", "Production"], default=["Staging", "Production"])
        with colf2:
            offer_filter = st.text_input("Offer ID contains")
        with colf3:
            url_filter = st.text_input("URL contains")
        with colf4:
            date_range = st.date_input("Expired Date Range",
                                       value=(datetime(selected_year, 1, 1), datetime(selected_year, 12, 31)),
                                       key="date_range")

        # Apply filters
        df = combined[combined["year"] == selected_year]
        if env_filter:
            df = df[df["env"].isin(env_filter)]
        if offer_filter:
            df = df[df["mappedOfferId"].astype(str).str.contains(offer_filter, case=False, na=False)]
        if url_filter:
            df = df[df["videoURL"].str.contains(url_filter, case=False, na=False)]
        if len(date_range) == 2:
            df = df[(df["date"] >= date_range[0]) & (df["date"] <= date_range[1])]

        # Display table with click-to-modal
        if not df.empty:
            # Create a clickable column
            df_display = df[["env", "mappedOfferId", "videoURL", "expired"]].copy()
            df_display["View All"] = "Click to see all URLs"

            # Use st.dataframe with on_select
            selection = st.dataframe(
                df_display.sort_values(["env", "expired"]),
                use_container_width=True,
                height=700,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )

            if selection.selection.rows:
                idx = selection.selection.rows[0]
                selected_row = df_display.iloc[idx]
                offer_id = selected_row["mappedOfferId"]

                # Modal: Show ALL URLs with this offer ID in the selected year
                with st.expander(f"All URLs for Offer ID: {offer_id}", expanded=True):
                    full_list = combined[
                        (combined["mappedOfferId"] == offer_id) &
                        (combined["year"] == selected_year)
                        ][["env", "videoURL", "expired"]].sort_values("env")

                    st.dataframe(full_list, use_container_width=True, height=400)
                    st.caption(f"{len(full_list)} URL(s) found for this offer")
        else:
            st.info("No URLs match the current filters.")

    # === TAB 3: Deep Diff (by Year) ===
    with tab3:
        stag_year = stag[stag["year"] == selected_year]
        prod_year = prod[prod["year"] == selected_year]

        only_stag = stag_year[~stag_year["videoURL"].isin(prod_year["videoURL"])]
        only_prod = prod_year[~prod_year["videoURL"].isin(stag_year["videoURL"])]

        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Only in Staging ({selected_year})")
            st.metric("Count", len(only_stag))
            st.dataframe(only_stag[["mappedOfferId", "videoURL", "expired"]], height=600)
        with col2:
            st.subheader(f"Only in Production ({selected_year})")
            st.metric("Count", len(only_prod))
            st.dataframe(only_prod[["mappedOfferId", "videoURL", "expired"]], height=600)

    # === TAB 4: URL Health ===
    with tab4:
        if st.button("Run Health Check", type="primary", use_container_width=True):
            with st.spinner("Checking URLs..."):
                # Simple version without cache for demo
                urls = combined["videoURL"].dropna().unique()
                results = []
                for url in st.progress(urls):
                    try:
                        r = requests.head(url, timeout=8)
                        results.append({"videoURL": url, "alive": r.status_code < 400})
                    except:
                        results.append({"videoURL": url, "alive": False})
                st.session_state.health = pd.DataFrame(results)
            st.success("Done!")

        if "health" in st.session_state:
            df = st.session_state.health
            st.write(f"**{len(df)} URLs** → **{df['alive'].sum()} alive**")
            st.dataframe(df.style.apply(lambda r: ["background:#d4edda" if r.alive else "#f8d7da"] * 2, axis=1))

    st.markdown("<div class='footer'>Filters + Click-to-Modal + Year Deep Diff • Auto-deploy ready</div>",
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
