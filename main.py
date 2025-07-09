import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ENDPOINT = os.getenv("API_ENDPOINT")
API_OFFER_LINK = os.getenv("API_OFFER_LINK")

ORIGIN = "SCL"

# Calculate current date and 9 months ahead
MONTH_THRESHOLD = 9
current_date = datetime.now()
end_date = current_date + timedelta(days=30 * MONTH_THRESHOLD)

# Format for API calls
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    await update.message.reply_text(
        "Welcome Aboard! 👨‍✈️ find the best flight prices to popular destinations in Europe 🇪🇺\n\n"
        "Use /flight to see available destinations ✈️",
    )


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show destination options as inline buttons."""
    keyboard = []
    row = []

    for i, destination in enumerate(top_destinations):
        row.append(
            InlineKeyboardButton(
                destination["name"], callback_data=f"destination_{destination['code']}"
            )
        )

        # Create a new row every 2 buttons for better layout
        if len(row) == 2 or i == len(top_destinations) - 1:
            keyboard.append(row)
            row = []

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Selecciona un destino para buscar vuelos:",
        reply_markup=reply_markup,
    )


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the user's chat ID."""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"Tu Chat ID es: `{chat_id}`", parse_mode="Markdown"
    )


async def handle_destination_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle destination selection callback."""

    await update.callback_query.message.reply_text(
        "Buscando ofertas ✈️\n\nEsto puede tardar unos segundos... ⏳",
    )

    query = update.callback_query
    await query.answer()

    # Extract destination code from callback data
    destination_code = query.data.replace("destination_", "")
    destination_country = next(
        filter(lambda x: x["code"] == destination_code, top_destinations)
    )["name"]

    print(
        f"Fetching data for destination: {destination_country} ({destination_code})... ⏳"
    )

    try:
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

        # Check multiple months to find the best offer
        best_price = None
        best_date = None
        best_month = None
        best_year = None

        # Generate list of months to check (current to MONTH_THRESHOLD months ahead)
        months_to_check = []
        current = datetime.now()
        for i in range(MONTH_THRESHOLD):
            check_date = current + timedelta(days=30 * i)
            months_to_check.append(
                {"month": check_date.strftime("%m"), "year": check_date.strftime("%Y")}
            )

        for month_data in months_to_check:
            params = {
                "triptype": "RT",
                "origin": ORIGIN,
                "destination": destination_code,
                # "outboundDate": f"{YEAR}-{MONTH}-01",
                "month": month_data["month"],
                "year": month_data["year"],
                "currencyCode": "USD",
            }

            print(f"Checking month: {month_data['month']}/{month_data['year']}")

            response = requests.get(
                API_ENDPOINT, params=params, headers=headers, timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                print("Data fetched successfully! ✈️")

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

                        # Update best price if this is better
                        if best_price is None or min_price["price"] < best_price:
                            best_price = min_price["price"]
                            best_date = min_price["date"]
                            best_month = month_data["month"]
                            best_year = month_data["year"]

            time.sleep(0.5)

        if best_price is not None:
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

            message = "* 🚨 ALERTA DE PRECIO BAJO 🚨 *\n\n"
            message += f"✈️ *Ruta:* {ORIGIN} → {destination_code}\n"
            message += f"📅 *Mes:* {month_name} {best_year}\n"
            message += f"📆 *Fecha del vuelo:* {best_date}\n"
            message += f"💸 *Precio:* ${best_price} USD\n\n"

            year, month, day = best_date.split("-")

            # Calculate date 7 days after
            start_range_date = datetime(int(year), int(month), int(day))
            end_range_date = start_range_date + timedelta(days=7)

            # Format dates for URL
            start_date_str = start_range_date.strftime("%Y-%m-%d")
            end_date_str = end_range_date.strftime("%Y-%m-%d")

            message += f"🔗 [¡Reserva tu vuelo! 🛫🛫]({API_OFFER_LINK}?o1={ORIGIN}&d1={destination_code}&dd1={start_date_str}&dd2={end_date_str}&ADT=1&CHD=0&INL=0&r=true&mm=true&forcedCurrency=USD&forcedCulture=es-ES&newecom=true"

            await query.message.reply_text(message, parse_mode="Markdown")
        else:
            await query.message.reply_text(
                f"No se encontraron precios para {destination_country}, intenta otro mes o año ✨"
            )
    except Exception as e:
        print(f"Error: {e}")
        await query.message.reply_text(
            "Something went wrong while fetching our service 😔"
        )


def main() -> None:
    """Start FLY bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("flight", search))
    application.add_handler(CommandHandler("chatid", get_chat_id))
    application.add_handler(CallbackQueryHandler(handle_destination_callback))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
