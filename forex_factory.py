import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time
import random

def get_high_impact_news():
    """Fetch high impact news from Forex Factory calendar"""
    url = "https://www.forexfactory.com/calendar?week=this"

    try:
        # More sophisticated headers to mimic a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }

        # Create a session for better handling
        session = requests.Session()

        # Add a small random delay
        time.sleep(random.uniform(1, 3))

        # Send request with session
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all calendar rows
        calendar_rows = soup.find_all('tr', class_='calendar_row')
        high_impact_news = []

        for row in calendar_rows:
            # Check impact level (red = high impact)
            impact = row.find('span', class_='impact')
            if impact and 'high' in str(impact).lower():

                # Extract date
                date_div = row.find('td', class_='calendar__date')
                if date_div:
                    date_str = date_div.text.strip()
                else:
                    continue

                # Extract time
                time_div = row.find('td', class_='calendar__time')
                time_str = time_div.text.strip() if time_div else "All Day"

                # Extract currency and event
                currency_div = row.find('td', class_='calendar__currency')
                currency = currency_div.text.strip() if currency_div else ""

                event_div = row.find('td', class_='calendar__event')
                event = event_div.text.strip() if event_div else ""

                # Extract actual, forecast and previous values
                actual_div = row.find('td', class_='calendar__actual')
                actual = actual_div.text.strip() if actual_div else "Pending"

                forecast_div = row.find('td', class_='calendar__forecast')
                forecast = forecast_div.text.strip() if forecast_div else "N/A"

                previous_div = row.find('td', class_='calendar__previous')
                previous = previous_div.text.strip() if previous_div else "N/A"

                # Add to list
                high_impact_news.append({
                    'date': date_str,
                    'time': time_str,
                    'currency': currency,
                    'event': event,
                    'actual': actual,
                    'forecast': forecast,
                    'previous': previous
                })

        return high_impact_news
    except Exception as e:
        print(f"Error fetching Forex Factory data: {str(e)}")
        return []