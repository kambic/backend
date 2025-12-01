import json
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time
import io

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

    /* Style for the global selector container */
    .global-selector-container {
        padding: 10px 0 10px 0;
        border-bottom: 2px solid #eee;
        margin-bottom: 10px;
    }
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
            # Create mock files if they don't exist for running the app
            if file_path == "mtcms-stag-response.json":
                mock_data = [
                                {"mappedOfferId": f"S{i}",
                                 "videoURLs": [{"videoURL": f"https://mock-stag.com/video{i}"}],
                                 "expired": f"2023-01-{i % 28 + 1:02d}T00:00:00Z"} for i in range(1, 201)
                            ] + [
                                {"mappedOfferId": f"S{i}",
                                 "videoURLs": [{"videoURL": f"https://mock-stag.com/video{i}"}],
                                 "expired": f"2024-05-{i % 28 + 1:02d}T00:00:00Z"} for i in range(201, 301)
                            ]
            else:
                mock_data = [
                                {"mappedOfferId": f"P{i}",
                                 "videoURLs": [{"videoURL": f"https://mock-prod.com/video{i}"}],
                                 "expired": f"2023-01-{i % 28 + 1:02d}T00:00:00Z"} for i in range(1, 151)
                            ] + [
                                {"mappedOfferId": f"P{i}",
                                 "videoURLs": [{"videoURL": f"https://mock-prod.com/video{i}"}],
                                 "expired": f"2024-05-{i % 28 + 1:02d}T00:00:00Z"} for i in range(151, 251)
                            ]

            # Write mock data to file
            with open(path, 'w') as f:
                json.dump(mock_data, f)
            st.warning(f"Mock data created for {path} as file was not found.")

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
        df["is_alive"] = None  # Column for validation results

        return df.drop(columns=["videoURLs"], errors="ignore")


# ========================= URL VALIDATOR CLASS =========================
class URLValidator:
    @staticmethod
    def check_single_url(url_data: dict) -> dict:
        """Checks the HTTP status of a single URL."""
        url = url_data["videoURL"]
        try:
            start = time.time()
            # Using requests.head is faster than requests.get as it doesn't download the body
            resp = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "Streamlit-Dashboard"})
            rt = int((time.time() - start) * 1000)
            return {
                "videoURL": url,
                "status_code": resp.status_code,
                # Consider 2xx and 3xx as alive
                "alive": 200 <= resp.status_code < 400,
                "response_time_ms": rt
            }
        except Exception:
            # Handle connection errors, timeouts, etc.
            return {
                "videoURL": url,
                "status_code": "Error/Timeout",
                "alive": False,
                "response_time_ms": None
            }

    @classmethod
    def validate_all(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Validates all unique URLs in the DataFrame using parallel threads."""
        # We only need one entry per unique URL for validation
        unique_urls = (
            df[["videoURL", "env"]]
            .dropna(subset=["videoURL"])
            .drop_duplicates(subset=["videoURL"])
            .to_dict("records")
        )

        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        total_urls = len(unique_urls)
        with ThreadPoolExecutor(max_workers=25) as executor:
            # Create futures for each URL check
            futures = {executor.submit(cls.check_single_url, row): row for row in unique_urls}

            for i, future in enumerate(as_completed(futures)):
                try:
                    results.append(future.result())
                except Exception as e:
                    st.error(f"Error checking URL: {e}")

                # Update progress bar and status text
                progress_value = (i + 1) / total_urls
                progress_bar.progress(progress_value)
                status_text.text(f"Validating... {i + 1}/{total_urls}")

        progress_bar.empty()
        status_text.empty()
        return pd.DataFrame(results)


# ========================= MAIN DASHBOARD CLASS =========================
class ExpiredURLsComparator:
    def __init__(self):
        self.df_stag = DataLoader.load_environment("mtcms-stag-response.json", "Staging")
        self.df_prod = DataLoader.load_environment("mtcms-prod-response.json", "Production")
        # Base combined DataFrame (without validation results yet)
        self.df_combined = pd.concat([self.df_stag, self.df_prod], ignore_index=True)
        self.df_analysis = self._get_analysis_df()  # This will hold the final data for charts

    def _get_analysis_df(self):
        """Prepares the final DataFrame for analysis, merging validation results if available."""
        df = self.df_combined.copy()

        # If validation results exist, merge them back into the main DataFrame
        if "validation_results" in st.session_state and not st.session_state.validation_results.empty:
            df_val = st.session_state.validation_results.rename(
                columns={"status_code": "http_status_val", "alive": "is_alive_val"}
            )

            # Merge the validation status back based on the unique URL.
            df = pd.merge(
                df,
                df_val[["videoURL", "http_status_val", "is_alive_val", "response_time_ms"]],
                on="videoURL",
                how="left"
            )

            # Use the validated status/alive columns where available
            df["status_checked"] = df["is_alive_val"].notna()
            df["http_status"] = df["http_status_val"].combine_first(df["http_status"])
            df["is_alive"] = df["is_alive_val"].combine_first(df["is_alive"])

        # Add month column for new analysis
        df["month"] = df["expired"].dt.month
        # Create a period/string column for monthly grouping and plotting
        df["month_year_str"] = df["expired"].dt.to_period("M").astype(str)
        return df

    def render_header_metrics(self):
        col1, col2, col3, col4 = st.columns(4)

        # Use the base data length for the primary metrics
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

    def render_time_series_analysis(self, selected_year):
        """Renders charts for yearly and monthly aggregations, enhanced with status if validated."""
        st.header("Expired URLs Time Series")

        # --- Aggregation by Year (Original, enhanced with Status if available) ---
        st.subheader("Count by Expiration Year Breakdown (All Years)")

        # Check if we have status data to enrich the chart
        has_status_data = self.df_analysis["status_checked"].any()

        group_cols = ["year", "env"]
        if has_status_data:
            st.caption("Broken/Alive status is shown if URL validation was performed in the Validator tab.")
            # Convert boolean status to descriptive string for better chart labels
            status_col = self.df_analysis["is_alive"].fillna('N/A').astype(str).replace(
                {'True': 'Alive (2xx/3xx)', 'False': 'Broken (4xx/Error)'})
            group_cols.append(status_col.name)

            yearly = self.df_analysis.groupby(group_cols, as_index=False).size()
            yearly.columns = ["year", "env", "Status", "count"]
            color_map = {'Alive (2xx/3xx)': '#4ECDC4', 'Broken (4xx/Error)': '#FF6B6B', 'N/A': '#ccc'}
            color_label = "Status"
            barmode = "stack"
        else:
            yearly = self.df_analysis.groupby(group_cols, as_index=False).size()
            yearly.columns = ["year", "env", "count"]
            color_map = {"Staging": "#FF6B6B", "Production": "#4ECDC4"}
            color_label = "env"
            barmode = "group"

        fig_year = px.bar(
            yearly,
            x="year",
            y="count",
            color=color_label,
            barmode=barmode,
            text="count",
            color_discrete_map=color_map,
            labels={"count": "Expired URLs", "year": "Expiration Year"},
            title="Expired URLs per Year – Staging vs Production"
        )
        fig_year.update_traces(textposition="outside")
        st.plotly_chart(fig_year, use_container_width=True, width='stretch')

        # --- Aggregation by Month (Now controlled by the global selector) ---
        st.markdown("---")
        st.subheader(f"Monthly Trend Drilldown for Year {selected_year}")

        monthly_data = self.df_analysis[self.df_analysis["year"] == selected_year]
        if monthly_data.empty:
            st.info(f"No expired URLs found for the selected year {selected_year}.")
            return

        monthly_grouped = monthly_data.groupby(["month_year_str", "env"], as_index=False).size()
        monthly_grouped.columns = ["month_year_str", "env", "count"]

        fig_month = px.line(
            monthly_grouped,
            x="month_year_str",
            y="count",
            color="env",
            color_discrete_map={"Staging": "#FF6B6B", "Production": "#4ECDC4"},
            markers=True,
            title=f"Monthly Expired URL Trend in {selected_year}"
        )
        fig_month.update_xaxes(title_text="Month of Expiration", categoryorder='category ascending')
        fig_month.update_yaxes(title_text="Expired URLs Count")
        st.plotly_chart(fig_month, use_container_width=True)

    def render_drilldown_tab(self, selected_year):
        """Renders the detailed tables for the globally selected year."""
        st.header(f"Detailed Drill Down: {selected_year} Expired URLs")

        col1, col2 = st.columns(2)

        # Columns to display in the drilldown table, including new status columns
        analysis_cols = ["mappedOfferId", "videoURL", "expired", "http_status", "is_alive", "response_time_ms"]

        stag_data = self.df_analysis[
            (self.df_analysis["year"] == selected_year) &
            (self.df_analysis["env"] == "Staging")
            ][analysis_cols]

        prod_data = self.df_analysis[
            (self.df_analysis["year"] == selected_year) &
            (self.df_analysis["env"] == "Production")
            ][analysis_cols]

        with col1:
            st.subheader("Staging Data")
            st.dataframe(stag_data, use_container_width=True, height=400)
            st.caption(f"{len(stag_data)} URLs in Staging for {selected_year}")

        with col2:
            st.subheader("Production Data")
            st.dataframe(prod_data, use_container_width=True, height=400)
            st.caption(f"{len(prod_data)} URLs in Production for {selected_year}")

    def render_diff_detective_tab(self):
        # Identify URLs present in one environment but not the other
        stag_only = self.df_analysis[
            (self.df_analysis["env"] == "Staging") &
            (~self.df_analysis["videoURL"].isin(self.df_analysis[self.df_analysis["env"] == "Production"]["videoURL"]))
            ].drop_duplicates(subset=["videoURL"])

        prod_only = self.df_analysis[
            (self.df_analysis["env"] == "Production") &
            (~self.df_analysis["videoURL"].isin(self.df_analysis[self.df_analysis["env"] == "Staging"]["videoURL"]))
            ].drop_duplicates(subset=["videoURL"])

        c1, c2 = st.columns(2)
        # Added response_time_ms for more data, and preparing to use a larger table size
        display_cols = ["mappedOfferId", "videoURL", "expired", "http_status", "is_alive", "response_time_ms"]

        with c1:
            st.subheader("Only in Staging (false positives?)")
            if len(stag_only) > 0:
                # Increased height for a bigger table
                st.dataframe(stag_only[display_cols], use_container_width=True, height=600)
                st.error(f"{len(stag_only)} Unique URLs")
            else:
                st.success("No extra URLs")

        with c2:
            st.subheader("Only in Production (data drift!)")
            if len(prod_only) > 0:
                # Increased height for a bigger table
                st.dataframe(prod_only[display_cols], use_container_width=True, height=600)
                st.warning(f"{len(prod_only)} Unique URLs – investigate!")
            else:
                st.success("Perfectly synced")

    def render_validator_export_tab(self):
        st.subheader("Live URL Validation + Export Report")
        st.info("Validation results are stored for the current session and used in the analysis tabs.")

        if st.button("Validate All Unique URLs Now!", type="primary"):
            # The validation only needs to run on the base combined DF as it extracts unique URLs
            with st.spinner("Checking unique URLs in parallel..."):
                validated_df = URLValidator.validate_all(self.df_combined)
                st.session_state.validation_results = validated_df
                # Rerun to update analysis data across all tabs
                st.rerun()

        if "validation_results" in st.session_state and not st.session_state.validation_results.empty:
            df_val = st.session_state.validation_results
            alive = df_val["alive"].sum()

            st.write(f"Total Unique URLs checked: **{len(df_val)}**")
            st.write(f"Alive (2xx/3xx): **{alive}** | Dead/Broken (4xx/Error/Timeout): **{len(df_val) - alive}**")

            # Color styling for the table
            def highlight_row(row):
                # Only apply highlighting if 'alive' is not None (i.e., successfully checked)
                if row.alive is True:
                    return ["background-color: #d4edda"] * len(row)
                elif row.alive is False:
                    return ["background-color: #f8d7da"] * len(row)
                return [""] * len(row)

            styled = df_val.style.apply(highlight_row, axis=1)
            st.dataframe(styled, use_container_width=True, height=500)

            # Export options
            col1, col2, col3 = st.columns(3)

            # CSV export
            csv = df_val.to_csv(index=False).encode('utf-8')

            # Excel export
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df_val.to_excel(writer, sheet_name='URL Health Report', index=False)
            excel_data = buffer.getvalue()

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
        st.title("STAG vs PROD Expired URLs Battle Arena")

        # Re-get the analysis DF every run to check for new session state changes (validation results)
        self.df_analysis = self._get_analysis_df()

        self.render_header_metrics()
        st.markdown("---")

        # --- GLOBAL YEAR SELECTION ---
        years = sorted(self.df_analysis["year"].unique(), reverse=True)
        if years:
            # Set default year to the latest available year
            default_year_index = years.index(max(years)) if max(years) in years else 0

            st.markdown('<div class="global-selector-container">', unsafe_allow_html=True)
            col_sel, _ = st.columns([1, 4])
            with col_sel:
                selected_year = st.selectbox(
                    "Select Expiration Year Focus",
                    years,
                    index=default_year_index,
                    key="global_year_selector",
                    help="Filter charts and drill-down tables by this expiration year."
                )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("No expiration year data found in the files.")
            return

        # --- TABS ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "Time Series Analysis",
            "Drill Down",
            "Diff Detective",
            "Validator & Export"
        ])

        with tab1:
            self.render_time_series_analysis(selected_year)

        with tab2:
            self.render_drilldown_tab(selected_year)

        with tab3:
            self.render_diff_detective_tab()

        with tab4:
            self.render_validator_export_tab()

        st.markdown("<div class='footer'>Made with Streamlit • Global Year Filtering • Enhanced Time Series</div>",
                    unsafe_allow_html=True)


# ========================= RUN APP =========================
if __name__ == "__main__":
    try:
        dashboard = ExpiredURLsComparator()
        dashboard.run()
    except Exception as e:
        # Catch exceptions during initialization or run
        st.error(f"An error occurred: {e}")
        st.stop()
