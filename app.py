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
        width: 100% !important;
    }
    .stSelectbox {
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def create_tradingview_chart(symbol, timeframe, container_id):
    """Creates a TradingView chart widget with error handling"""
    # Special handling for XAUUSD
    if symbol == "XAUUSD":
        tv_symbol = "CAPITALCOM:GOLD"
    else:
        # Remove '=X' suffix for regular forex pairs
        tv_symbol = symbol.replace('=X', '')
        tv_symbol = f"FX:{tv_symbol}"

    chart_html = f"""
        <div class="tradingview-widget-container">
            <div id="{container_id}"></div>
            <div class="tradingview-widget-copyright">
                <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
                    <span class="blue-text">Track all markets on TradingView</span>
                </a>
            </div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
                "width": "100%",
                "height": 400,
                "symbol": "{tv_symbol}",
                "interval": "{timeframe}",
                "timezone": "Etc/UTC",
                "theme": "light",
                "style": "1",
                "locale": "en",
                "enable_publishing": false,
                "allow_symbol_change": true,
                "container_id": "{container_id}",
                "studies": [
                    {{"id": "MAExp@tv-basicstudies", "inputs": {{"length": 21}}}}
                ]
            }});
            </script>
        </div>
    """
    return chart_html

def main():
    st.title("📈 Live Forex Chart Viewer")

    # Auto-refresh status
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now().strftime('%H:%M:%S')

    st.sidebar.write('Charts update automatically every second')
    st.sidebar.write('Last update: ' + st.session_state.last_update)

    # Economic Calendar
    st.header("📅 Economic Calendar")
    calendar_html = """
        <div class="tradingview-widget-container">
            <div class="tradingview-widget-container__widget"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
            {
                "width": "100%",
                "height": "400",
                "colorTheme": "light",
                "isTransparent": false,
                "locale": "en",
                "importanceFilter": "0,1,2",
                "currencyFilter": "USD,EUR,JPY,GBP,AUD,CAD,CHF,NZD"
            }
            </script>
        </div>
    """
    st.components.v1.html(calendar_html, height=450)
    
    st.markdown("---")

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
        # Create three columns for the charts
        col1, col2, col3 = st.columns(3)

        # Timeframe configurations
        timeframes = [
            {"interval": "5", "title": "5 Minutes"},
            {"interval": "60", "title": "1 Hour"},
            {"interval": "D", "title": "Daily"}
        ]

        # Display charts in columns with titles
        with col1:
            st.subheader("5 Minutes Chart")
            st.components.v1.html(
                create_tradingview_chart(selected_pair, timeframes[0]["interval"], "chart1"),
                height=450
            )

        with col2:
            st.subheader("1 Hour Chart")
            st.components.v1.html(
                create_tradingview_chart(selected_pair, timeframes[1]["interval"], "chart2"),
                height=450
            )

        with col3:
            st.subheader("Daily Chart")
            st.components.v1.html(
                create_tradingview_chart(selected_pair, timeframes[2]["interval"], "chart3"),
                height=450
            )

        # Market Sentiment Section
        st.markdown("---")
        st.header(f"📊 Market Sentiment Analysis - {selected_pair}")
        
        # Create two columns for better layout
        sent_col1, sent_col2 = st.columns(2)
        
        with sent_col1:
            st.subheader("1. Global Market Sentiment")
            st.markdown("""
                - Overall Market Mood: 📈 Bullish
                - Risk Sentiment: Neutral
                - Market Volatility: Moderate
            """)
            
            st.subheader("2. Key Economic Data and Calendar")
            st.markdown("Recent and upcoming high-impact events:")
            st.components.v1.html("""
                <div style="border:1px solid #ccc; padding:10px; border-radius:5px;">
                    • CPI Data Release (Tomorrow)<br>
                    • Central Bank Meeting (Next Week)<br>
                    • NFP Report (Friday)
                </div>
            """, height=100)

            st.subheader("3. Technical Analysis")
            st.markdown("""
                - Trend Direction: Upward
                - Key Support: 1.2340
                - Key Resistance: 1.2460
                - Moving Averages: Above 200 EMA
            """)

        with sent_col2:
            st.subheader("4. USD and Bond Yields")
            st.markdown("""
                - USD Index: Weakening
                - 10Y Treasury Yield: 4.2%
                - Rate Expectations: Stable
            """)
            
            st.subheader("5. News and Sentiment")
            st.markdown("""
                - Market Headlines:
                    * Central Bank Commentary
                    * Economic Growth Data
                    * Geopolitical Updates
            """)
            
            st.subheader("6. Trade Plan and Strategy")
            st.markdown("""
                - Entry Zones: 1.2350-1.2380
                - Stop Loss: 1.2320
                - Take Profit: 1.2450
                - Risk Management: 1% per trade
            """)

        # Update timestamp every second
        st.session_state.last_update = datetime.now().strftime('%H:%M:%S')
        time.sleep(1)
        st.rerun()

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.warning("Please try selecting a different pair or refresh the page.")

if __name__ == "__main__":
    main()