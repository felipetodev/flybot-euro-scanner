# ✈️ FlyBot Euro Scanner

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Flight Price Notification](https://github.com/felipetodev/flybot-euro-scanner/actions/workflows/flight-price-notification.yml/badge.svg)](https://github.com/felipetodev/flybot-euro-scanner/actions/workflows/flight-price-notification.yml)

Telegram bot that monitors flight prices from Santiago, Chile (SCL) to popular European destinations and sends automatic notifications when great deals are found.

## 🚀 Features

### Interactive Telegram Bot (`main.py`)
- **Real-time Flight Search**: Search flights to 7 popular European destinations
- **Smart Price Comparison**: Scans 9 months of data to find the best prices
- **Interactive Interface**: Easy-to-use inline keyboard buttons
- **Instant Results**: Get flight prices and booking links immediately

### Automated Price Monitoring (`cron_notification.py`)
- **Scheduled Monitoring**: Automatically checks prices every 12 hours
- **Deal Alerts**: Sends notifications when flights under $400 USD are found
- **Best Price Tracking**: Finds the lowest price across 9 months for each destination
- **Smart Notifications**: Only alerts for genuine deals below your threshold

## 🤖 Bot Commands

- `/start` - Welcome message and instructions
- `/flight` - Browse available destinations
- `/chatid` - Get your Telegram Chat ID

## ⚙️ GitHub Actions Automation

The bot includes automated price monitoring using GitHub Actions:

- **Schedule**: Runs every 12 hours (00:00 and 12:00 UTC)
- **Manual Trigger**: Can be triggered manually from the Actions tab
- **Environment**: Uses GitHub repository secrets for configuration
- **Notifications**: Sends Telegram alerts for deals under specified price threshold

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Support

Was this project helpful? Please give it a star! ⭐
