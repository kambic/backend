# app.py
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional
import time

# ========================= CONFIG & STYLING =========================
st.set_page_config(
    page_title="STAG vs PROD – Expired URLs Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .big-font { font-size: 26px !important; font-weight: bold; }
    .metric-good { color: #00ff00; }
    .metric-bad { color: #ff3333; }
    .url-alive { background-color: #d4edda; color: #155724; padding: 2px 6px; border-radius: 4px; }
    .url-dead { background-color: #f8d7da; color: #721c24; padding: 2px 6px; border-radius: 4px; }
    .footer { text-align: center; color: #888; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)


# ========================= DATA LOADER CLASS =========================
class DataLoader:
    @staticmethod
    @st.cache_data(ttl=600, show_spinner=False)
    def load_environment(file_path: str, env_name: str) -> pd.DataFrame:
        """Load and preprocess JSON response from one environment."""
        path = Path(file_path)
        if not path.exists():
            st.error(f"File not found: {path}")
            st.stop()

        with open(path) as f:
            data = json.load(f)

        df = pd.DataFrame(data)
        df["videoURL"] = df["videoURLs"].apply(lambda x: x[0]["videoURL"] if x else None)
        df["expired"] = pd.to_datetime(df["expired"])
        df["year"] = df["expired"].dt.year
        df["env"] = env_name
        df["status_checked"] = False
        df["http_status"] = None
        df["response_time_ms"] = None

        return df.drop(columns=["videoURLs"], errors="ignore")


# ========================= URL VALIDATOR CLASS =========================
class URLValidator:
    @staticmethod
    def check_single_url(url_data: dict) -> dict:
        url = url_data["videoURL"]
        try:
            start = time.time()
            resp = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "Streamlit-Dashboard"})
            rt = int((time.time() - start) * 1000)
            return {
                "mappedOfferId": url_data["mappedOfferId"],
                "videoURL": url,
                "env": url_data["env"],
                "status_code": resp.status_code,
                "alive": resp.status_code < 400,
                "response_time_ms": rt
            }
        except Exception:
            return {
                "mappedOfferId": url_data["mappedOfferId"],
                "videoURL": url,
                "env": url_data["env"],
                "status_code": "Error/Timeout",
                "alive": False,
                "response_time_ms": None
            }

    @classmethod
    def validate_all(cls, df: pd.DataFrame) -> pd.DataFrame:
        unique_urls = (
            df[["mappedOfferId", "videoURL", "env"]]
            .dropna(subset=["videoURL"])
            .drop_duplicates(subset=["videoURL"])
            .to_dict("records")
        )

        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = {executor.submit(cls.check_single_url, row): row for row in unique_urls}
            for i, future in enumerate(as_completed(futures)):
                results.append(future.result())
                progress_bar.progress((i + 1) / len(futures))
                status_text.text(f"Validating... {i + 1}/{len(unique_urls)}")

        progress_bar.empty()
        status_text.empty()
        return pd.DataFrame(results)


# ========================= MAIN DASHBOARD CLASS =========================
class ExpiredURLsComparator:
    def __init__(self):
        self.df_stag = DataLoader.load_environment("mtcms-stag-response.json", "Staging")
        self.df_prod = DataLoader.load_environment("mtcms-prod-response.json", "Production")
        self.df_combined = pd.concat([self.df_stag, self.df_prod], ignore_index=True)

    def render_header_metrics(self):
        col1, col2, col3, col4 = st.columns(4)
        diff = len(self.df_stag) - len(self.df_prod)
        diff_pct = (diff / len(self.df_prod) * 100) if len(self.df_prod) > 0 else 0

        with col1:
            st.metric("Staging Expired", len(self.df_stag))
        with col2:
            st.metric("Production Expired", len(self.df_prod), delta=f"{diff:+}")
        with col3:
            if abs(diff_pct) > 10:
                color = "metric-bad" if diff > 0 else "metric-good"
                st.markdown(f"<div class='{color} big-font'>{diff_pct:+.1f}% vs PROD</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='big-font'>{diff_pct:+.1f}% diff</div>", unsafe_allow_html=True)
        with col4:
            st.caption(f"Last refreshed: {datetime.now():%b %d, %Y %H:%M}")

    def render_yearly_chart(self):
        yearly = self.df_combined.groupby(["year", "env"], as_index=False).size()
        yearly.columns = ["year", "env", "count"]

        fig = px.bar(
            yearly,
            x="year",
            y="count",
            color="env",
            barmode="group",
            text="count",
            color_discrete_map={"Staging": "#FF6B6B", "Production": "#4ECDC4"},
            labels={"count": "Expired URLs"},
            title="Expired URLs per Year – Staging vs Production"
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True, width='stretch')

    def render_drilldown_tab(self):
        years = sorted(self.df_combined["year"].unique())
        selected_year = st.selectbox("Select Year", years, key="drilldown_year")

        col1, col2 = st.columns(2)
        stag_data = self.df_stag[self.df_stag["year"] == selected_year][["mappedOfferId", "videoURL", "expired"]]
        prod_data = self.df_prod[self.df_prod["year"] == selected_year][["mappedOfferId", "videoURL", "expired"]]

        with col1:
            st.subheader("Staging")
            st.dataframe(stag_data, width='stretch', height=400)
            st.caption(f"{len(stag_data)} URLs")

        with col2:
            st.subheader("Production")
            st.dataframe(prod_data, width='stretch', height=400)
            st.caption(f"{len(prod_data)} URLs")

    def render_diff_detective_tab(self):
        stag_only = self.df_stag[~self.df_stag["videoURL"].isin(self.df_prod["videoURL"])]
        prod_only = self.df_prod[~self.df_prod["videoURL"].isin(self.df_stag["videoURL"])]

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Only in Staging (false positives?)")
            if len(stag_only) > 0:
                st.dataframe(stag_only[["mappedOfferId", "videoURL", "expired"]], width='stretch')
                st.error(f"{len(stag_only)} URLs")
            else:
                st.success("No extra URLs")

        with c2:
            st.subheader("Only in Production (data drift!)")
            if len(prod_only) > 0:
                st.dataframe(prod_only[["mappedOfferId", "videoURL", "expired"]], width='stretch')
                st.warning(f"{len(prod_only)} URLs – investigate!")
            else:
                st.success("Perfectly synced")

    def render_validator_export_tab(self):
        st.subheader("Live URL Validation + Export Report")

        if st.button("Validate All Unique URLs Now!", type="primary"):
            with st.spinner("Checking hundreds of URLs in parallel..."):
                validated_df = URLValidator.validate_all(self.df_combined)
                st.session_state.validation_results = validated_df
            st.success(f"Validation complete! {len(validated_df)} URLs checked.")

        if "validation_results" in st.session_state and not st.session_state.validation_results.empty:
            df_val = st.session_state.validation_results
            alive = df_val["alive"].sum()

            st.write(f"Alive: **{alive}** | Dead/Broken: **{len(df_val) - alive}**")

            # Color styling
            def highlight_row(row):
                return ["background-color: #d4edda" if row.alive else "background-color: #f8d7da"] * len(row)
            styled = df_val.style.apply(highlight_row, axis=1)
            st.dataframe(styled, width='stretch', height=500)

            # Export
            col1, col2, col3 = st.columns(3)
            csv = df_val.to_csv(index=False).encode()
            excel_buffer = pd.ExcelWriter("url_health_report.xlsx", engine="openpyxl")
            df_val.to_excel(excel_buffer, index=False)
            excel_data = excel_buffer.buffer.getvalue()

            with col1:
                st.download_button("Download CSV", csv, "url_health_report.csv", "text/csv")
            with col2:
                st.download_button("Download Excel", excel_data, "url_health_report.xlsx",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with col3:
                if st.button("Clear Results"):
                    del st.session_state.validation_results
                    st.rerun()

    def run(self):
        st.title("STAG vs PROD Expired URLs")

        self.render_header_metrics()
        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs([
            "Yearly Overview",
            "Drill Down",
            "Diff Detective",
            "Validator & Export"
        ])

        with tab1:
            self.render_yearly_chart()

        with tab2:
            self.render_drilldown_tab()

        with tab3:
            self.render_diff_detective_tab()

        with tab4:
            self.render_validator_export_tab()

        st.markdown("<div class='footer'>Made with Streamlit • Parallel URL checks • Clean code</div>",
                    unsafe_allow_html=True)


# ========================= RUN APP =========================
if __name__ == "__main__":
    dashboard = ExpiredURLsComparator()
    dashboard.run()
