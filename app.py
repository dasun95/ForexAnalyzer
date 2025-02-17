import streamlit as st
import time
from datetime import datetime
from utils import get_forex_pairs, save_user_preference, get_last_user_preference, init_db

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="Forex Chart Viewer",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for TradingView widgets and layout
st.markdown("""
    <style>
    .tradingview-widget-container {
        height: 400px !important;
        margin-bottom: 20px;
    }
    .stSelectbox {
        margin-bottom: 20px;
    }
    iframe {
        width: 100%;
        height: 400px;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

def create_tradingview_chart(symbol, timeframe, container_id):
    """Creates a TradingView chart widget"""
    return f"""
        <div class="tradingview-widget-container" id="{container_id}">
            <div class="tradingview-widget-container__widget"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js">
            {{
                "width": "100%",
                "height": "400",
                "symbol": "FX:{symbol}",
                "interval": "{timeframe}",
                "timezone": "Etc/UTC",
                "theme": "light",
                "style": "1",
                "locale": "en",
                "enable_publishing": false,
                "allow_symbol_change": true,
                "support_host": "https://www.tradingview.com"
            }}
            </script>
        </div>
    """

def main():
    st.title("📈 Live Forex Chart Viewer")

    # Auto-refresh status
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now().strftime('%H:%M:%S')

    st.sidebar.write('Charts update automatically every second')
    st.sidebar.write('Last update: ' + st.session_state.last_update)

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

    try:
        # Remove '=X' suffix for TradingView
        symbol = selected_pair.replace('=X', '')

        # Create three columns for the charts
        col1, col2, col3 = st.columns(3)

        # Timeframe configurations
        timeframes = [
            {"interval": "5", "title": "5 Minutes"},
            {"interval": "60", "title": "1 Hour"},
            {"interval": "D", "title": "Daily"}
        ]

        # Display charts in columns
        with col1:
            st.markdown(create_tradingview_chart(symbol, timeframes[0]["interval"], "chart1"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_tradingview_chart(symbol, timeframes[1]["interval"], "chart2"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_tradingview_chart(symbol, timeframes[2]["interval"], "chart3"), unsafe_allow_html=True)

        # Update timestamp every second
        st.session_state.last_update = datetime.now().strftime('%H:%M:%S')
        time.sleep(1)
        st.rerun()

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.warning("Please try selecting a different pair or refresh the page.")

if __name__ == "__main__":
    main()