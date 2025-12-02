import pandas as pd
import streamlit as st
import plotly.express as px

# ------------------------------
# Data Loader Class
# ------------------------------
class ExpiredURLsData:
    def __init__(self, data):
        self.df = pd.DataFrame(data)
        self.prepare_data()

    def prepare_data(self):
        # Extract first video URL
        self.df['videoURL'] = self.df['videoURLs'].apply(lambda x: x[0]['videoURL'] if x else None)
        # Convert expired to datetime
        self.df['expired'] = pd.to_datetime(self.df['expired'])
        # Extract year for grouping
        self.df['year'] = self.df['expired'].dt.year
        # Keep relevant columns
        self.df = self.df[['mappedOfferId', 'videoURL', 'expired', 'year']]

    def get_grouped_data(self):
        return self.df.groupby('year').size().reset_index(name='count')

    def get_urls_by_year(self, year):
        return self.df[self.df['year'] == year][['mappedOfferId', 'videoURL', 'expired']]

# ------------------------------
# Dashboard Class
# ------------------------------
class ExpiredURLsDashboard:
    def __init__(self, data_loader: ExpiredURLsData):
        self.data_loader = data_loader
        self.grouped_data = self.data_loader.get_grouped_data()
        self.layout()

    def layout(self):
        st.title("📺 Expired URLs Dashboard")

        st.markdown("### Expired URLs per Year")
        self.plot_expired_chart()

        # Year selection
        selected_year = st.selectbox(
            "Select a Year to View Expired URLs",
            self.grouped_data['year']
        )

        self.show_urls_table(selected_year)

    def plot_expired_chart(self):
        fig = px.bar(
            self.grouped_data,
            x='year',
            y='count',
            text='count',
            labels={'count':'Number of Expired URLs', 'year':'Year'},
            color='count',
            color_continuous_scale='Reds',
            title="Expired URLs Grouped by Year"
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, width='stretch')  # updated best practice

    def show_urls_table(self, year):
        urls_df = self.data_loader.get_urls_by_year(year)
        st.markdown(f"### URLs Expired in {year}")
        st.dataframe(urls_df)

# ------------------------------
# Main Application
# ------------------------------
def main():
    # Sample JSON data (all expired)
    sample_data = [
        {"mappedOfferId": "VOD_CATALOGUE_1", "videoURLs": [{"videoURL": "rtsp://xx.ggg.tv:554/video1.ts"}], "expired": "2019-03-28T00:59:00.000Z"},
        {"mappedOfferId": "VOD_CATALOGUE_2", "videoURLs": [{"videoURL": "rtsp://xx.ggg.tv:554/video2.ts"}], "expired": "2020-11-15T12:00:00.000Z"},
        {"mappedOfferId": "VOD_CATALOGUE_3", "videoURLs": [{"videoURL": "rtsp://xx.ggg.tv:554/video3.ts"}], "expired": "2021-08-01T08:30:00.000Z"},
        {"mappedOfferId": "VOD_CATALOGUE_4", "videoURLs": [{"videoURL": "rtsp://xx.ggg.tv:554/video4.ts"}], "expired": "2022-01-10T10:00:00.000Z"},
        {"mappedOfferId": "VOD_CATALOGUE_5", "videoURLs": [{"videoURL": "rtsp://xx.ggg.tv:554/video5.ts"}], "expired": "2021-05-20T14:00:00.000Z"}
    ]

    # Initialize Data Loader
    data_loader = ExpiredURLsData(sample_data)

    # Initialize Dashboard
    ExpiredURLsDashboard(data_loader)

if __name__ == "__main__":
    main()
