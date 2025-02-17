import streamlit as st
import plotly.graph_objects as go
from utils import (
    get_forex_pairs, get_forex_data, format_price,
    init_db, save_user_preference, get_last_user_preference
)
import time

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="Forex Chart Viewer",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stPlotlyChart {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 10px;
    }
    .stSelectbox {
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def create_candlestick_chart(df, title):
    """Creates a candlestick chart using Plotly"""
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                        open=df['Open'],
                                        high=df['High'],
                                        low=df['Low'],
                                        close=df['Close'])])

    fig.update_layout(
        title=title,
        yaxis_title='Price',
        xaxis_title='Date',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        yaxis=dict(tickformat='.5f'),
        template='plotly_white'
    )

    return fig

def main():
    st.title("📈 Forex Chart Viewer")

    # Forex pair selection with last preference
    forex_pairs = get_forex_pairs()
    last_preference = get_last_user_preference()
    default_index = forex_pairs.index(last_preference) if last_preference in forex_pairs else 0

    selected_pair = st.selectbox(
        "Select Forex Pair",
        forex_pairs,
        index=default_index,
        help="Choose the currency pair you want to monitor"
    )

    # Save user preference
    save_user_preference(selected_pair)

    # Error container
    error_container = st.empty()

    try:
        # Create three columns for the charts
        col1, col2, col3 = st.columns(3)

        # Timeframe configurations
        timeframes = [
            {"interval": "5m", "period": "1d", "title": "5 Minutes"},
            {"interval": "1h", "period": "7d", "title": "1 Hour"},
            {"interval": "1d", "period": "60d", "title": "Daily"}
        ]

        # Display current price
        current_data = get_forex_data(selected_pair, "1m", "1d")
        current_price = current_data['Close'].iloc[-1]
        st.metric(
            label="Current Price",
            value=format_price(current_price)
        )

        # Create and display charts
        charts = []
        for tf in timeframes:
            with st.spinner(f'Loading {tf["title"]} chart...'):
                df = get_forex_data(
                    selected_pair,
                    tf["interval"],
                    tf["period"]
                )
                charts.append(create_candlestick_chart(
                    df,
                    f"{selected_pair} - {tf['title']} Chart"
                ))

        with col1:
            st.plotly_chart(charts[0], use_container_width=True)
        with col2:
            st.plotly_chart(charts[1], use_container_width=True)
        with col3:
            st.plotly_chart(charts[2], use_container_width=True)

        # Auto-refresh
        time.sleep(60)
        st.experimental_rerun()

    except Exception as e:
        error_container.error(f"Error: {str(e)}")
        st.warning("Please try selecting a different pair or wait a few minutes.")

if __name__ == "__main__":
    main()