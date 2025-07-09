import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_CHAT_ID = os.getenv("BOT_CHAT_ID")
API_ENDPOINT = os.getenv("API_ENDPOINT")
API_OFFER_LINK = os.getenv("API_OFFER_LINK")

SUBSCRIBED_USERS = [BOT_CHAT_ID]
PRICE_THRESHOLD = 400  # USD

ORIGIN = "SCL"
MONTH = "01"
YEAR = "2026"

top_destinations = [
    {"name": "Barcelona", "countryName": "España", "code": "BCN"},
    {"name": "Madrid", "countryName": "España", "code": "MAD"},
    {"name": "Paris", "countryName": "Francia", "code": "ORY"},
    {"name": "Roma", "countryName": "Italia", "code": "FCO"},
    {"name": "Milán", "countryName": "Italia", "code": "MXP"},
    {"name": "Lisboa", "countryName": "Portugal", "code": "LIS"},
    {"name": "Londres", "countryName": "Reino Unido", "code": "LHR"},
]


def send_telegram_message(chat_id, message):
    """Send a message to a specific chat ID."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print(f"Message sent to {chat_id}")
        else:
            print(f"Failed to send message to {chat_id}: {response.status_code}")
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")


def check_flight_prices():
    """Check flight prices and send notifications if prices are good."""
    headers = {
        "accept": "*/*",
        "accept-language": "es",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.34",
    }

    good_deals = []

    for destination in top_destinations:
        try:
            params = {
                "triptype": "RT",
                "origin": ORIGIN,
                "destination": destination["code"],
                "month": MONTH,
                "year": YEAR,
                "currencyCode": "USD",
            }

            response = requests.get(
                API_ENDPOINT, params=params, headers=headers, timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                if (
                    "data" in data
                    and "dayPrices" in data["data"]
                    and data["data"]["dayPrices"]
                ):
                    day_prices = data["data"]["dayPrices"]
                    valid_prices = [
                        price for price in day_prices if price.get("price") is not None
                    ]

                    if valid_prices:
                        min_price = min(
                            valid_prices, key=lambda x: x.get("price", float("inf"))
                        )

                        if min_price["price"] < PRICE_THRESHOLD:
                            good_deals.append(
                                {
                                    "destination": destination["name"],
                                    "code": destination["code"],
                                    "price": min_price["price"],
                                    "date": min_price["date"],
                                }
                            )

        except Exception as e:
            print(f"Error checking {destination['name']}: {e}")

    return good_deals


def main():
    """Main function to check prices and send notifications."""
    print(f"Checking flight prices at {datetime.now()}")

    good_deals = check_flight_prices()

    if good_deals and SUBSCRIBED_USERS:
        message = "🔥 ¡Ofertas de vuelos encontradas! 🔥\n\n"

        for deal in good_deals:
            start_date = datetime.strptime(deal["date"], "%Y-%m-%d")
            end_date = start_date + timedelta(days=7)

            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            message += f"✈️ {deal['destination']} ({deal['code']})\n"
            message += f"💰 ${deal['price']} USD\n"
            message += f"📅 {deal['date']}\n"
            message += f"[Ver vuelos]({API_OFFER_LINK}?o1={ORIGIN}&d1={deal['code']}&dd1={start_date_str}&dd2={end_date_str}&ADT=1)\n\n"

        # Send to all subscribed users
        for chat_id in SUBSCRIBED_USERS:
            send_telegram_message(chat_id, message)

    print(f"Notification check completed. Found {len(good_deals)} good deals.")


if __name__ == "__main__":
    main()
