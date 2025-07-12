import os
import time
from datetime import datetime, timedelta
import requests

if os.getenv("GITHUB_ACTIONS") != "true":
    from dotenv import load_dotenv

    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_CHAT_ID = os.getenv("BOT_CHAT_ID")
API_ENDPOINT = os.getenv("API_ENDPOINT")
API_OFFER_LINK = os.getenv("API_OFFER_LINK")

SUBSCRIBED_USERS = [BOT_CHAT_ID]
PRICE_THRESHOLD = 400  # USD

ORIGIN = "SCL"

MONTH_THRESHOLD = 9
current_date = datetime.now()
end_date = current_date + timedelta(days=30 * MONTH_THRESHOLD)

CURRENT_MONTH = current_date.strftime("%m")
CURRENT_YEAR = current_date.strftime("%Y")
END_MONTH = end_date.strftime("%m")
END_YEAR = end_date.strftime("%Y")

print(f"Checking flights from {CURRENT_MONTH}/{CURRENT_YEAR} to {END_MONTH}/{END_YEAR}")

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
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    }

    good_deals = []

    months_to_check = []
    current = datetime.now()
    for i in range(MONTH_THRESHOLD):
        check_date = current + timedelta(days=30 * i)
        months_to_check.append(
            {"month": check_date.strftime("%m"), "year": check_date.strftime("%Y")}
        )

    for destination in top_destinations:
        print(f"Checking {destination['name']} ({destination['code']})...")

        # Check multiple months to find the best offer for this destination
        best_price = None
        best_date = None
        best_month = None
        best_year = None

        try:
            for month_data in months_to_check:
                params = {
                    "triptype": "RT",
                    "origin": ORIGIN,
                    "destination": destination["code"],
                    "month": month_data["month"],
                    "year": month_data["year"],
                    "currencyCode": "USD",
                }

                print(f"  Checking month: {month_data['month']}/{month_data['year']}")

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
                            price
                            for price in day_prices
                            if price.get("price") is not None
                        ]

                        if valid_prices:
                            min_price = min(
                                valid_prices, key=lambda x: x.get("price", float("inf"))
                            )

                            # Update best price if this is better
                            if best_price is None or min_price["price"] < best_price:
                                best_price = min_price["price"]
                                best_date = min_price["date"]
                                best_month = month_data["month"]
                                best_year = month_data["year"]

                time.sleep(0.5)

            if best_price is not None and best_price < PRICE_THRESHOLD:
                month_names = {
                    "01": "Enero",
                    "02": "Febrero",
                    "03": "Marzo",
                    "04": "Abril",
                    "05": "Mayo",
                    "06": "Junio",
                    "07": "Julio",
                    "08": "Agosto",
                    "09": "Septiembre",
                    "10": "Octubre",
                    "11": "Noviembre",
                    "12": "Diciembre",
                }
                month_name = month_names.get(best_month, best_month)

                good_deals.append(
                    {
                        "destination": destination["name"],
                        "code": destination["code"],
                        "price": best_price,
                        "date": best_date,
                        "month": best_month,
                        "year": best_year,
                        "month_name": month_name,
                    }
                )

                print(f"  ✅ Good deal found: ${best_price} USD on {best_date}")
            else:
                print(f"  ❌ No good deals found (best price: ${best_price} USD)")

        except Exception as e:
            print(f"Error checking {destination['name']}: {e}")

    return good_deals


def main():
    """Main function to check prices and send notifications."""
    print(f"Checking flight prices at {datetime.now()}")
    print(f"Price threshold: ${PRICE_THRESHOLD} USD")
    print(
        f"Checking months from {CURRENT_MONTH}/{CURRENT_YEAR} to {END_MONTH}/{END_YEAR}"
    )

    good_deals = check_flight_prices()

    if good_deals and SUBSCRIBED_USERS:
        message = "🔥 ¡Ofertas de vuelos encontradas! 🔥\n\n"

        for deal in good_deals:
            # Calculate date 7 days after for URL range
            start_date = datetime.strptime(deal["date"], "%Y-%m-%d")
            end_date_range = start_date + timedelta(days=7)

            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date_range.strftime("%Y-%m-%d")

            message += f"✈️ *{deal['destination']}* ({deal['code']})\n"
            message += f"📅 *Mes:* {deal['month_name']} {deal['year']}\n"
            message += f"📆 *Fecha:* {deal['date']}\n"
            message += f"💰 *Precio:* ${deal['price']} USD\n"
            message += f"🔗 [Ver vuelos]({API_OFFER_LINK}?o1={ORIGIN}&d1={deal['code']}&dd1={start_date_str}&dd2={end_date_str}&ADT=1&CHD=0&INL=0&r=true&mm=true&forcedCurrency=USD&forcedCulture=es-ES&newecom=true)\n\n"

        # Send to all subscribed users
        for chat_id in SUBSCRIBED_USERS:
            send_telegram_message(chat_id, message)

        print(f"✅ Notification sent to {len(SUBSCRIBED_USERS)} users")
    else:
        print("❌ No good deals found or no subscribed users")

    print(f"Notification check completed. Found {len(good_deals)} good deals.")


if __name__ == "__main__":
    main()
