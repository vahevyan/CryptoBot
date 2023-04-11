
# IMPORTS

import telebot
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from io import BytesIO

# BOT TOKEN

bot = telebot.TeleBot('6004353621:AAGwlfwv5F9Z-hzPgBv4VkC94WrxNLKcVNc')

cryptos = ['BTC', 'ETH', 'DOGE', 'LTC', 'XRP']


def get_crypto_rate(crypto):
    ticker = yf.Ticker(f'{crypto}-USD')
    rate = ticker.info['regularMarketPrice']
    return rate


def get_crypto_history(crypto, days):
    ticker = yf.Ticker(f'{crypto}-USD')
    history = ticker.history(period=f'{days}d')
    return history


calculating = True
last_command = ''


# START COMMAND AND BUTTOMS

@bot.message_handler(commands=['start'])
def handle_start(message):
    global last_command
    last_command = 'start'
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3)
    buttons = [telebot.types.KeyboardButton(crypto) for crypto in cryptos]
    buttons.append(telebot.types.KeyboardButton('All Cryptos'))
    buttons.append(telebot.types.KeyboardButton('Graph'))
    buttons.append(telebot.types.KeyboardButton('Support'))
    buttons.append(telebot.types.KeyboardButton('Calculator'))
    markup.add(*buttons)

    # START MESSAGE

    bot.send_message(message.chat.id, "Here are available commands. Choose from them!", reply_markup=markup)


# FOR SENDING CRYPTO VALUES WITH DATE AND TIME

@bot.message_handler(func=lambda message: message.text in cryptos)
def handle_crypto(message):
    global last_command
    last_command = 'crypto'
    crypto = message.text
    rate = get_crypto_rate(crypto)
    message_text = f'{crypto}: ${rate:.2f}\nLast updated: {datetime.now()}'
    bot.send_message(message.chat.id, message_text)


# FUNCTION FOR 'All Cryptos' BUTTOM

@bot.message_handler(func=lambda message: message.text == 'All Cryptos')
def handle_all(message):
    global last_command
    last_command = 'all'
    message_text = ''
    for crypto in cryptos:
        rate = get_crypto_rate(crypto)
        message_text += f'{crypto}: ${rate:.2f}\n'
    message_text += f'Last updated: {datetime.now()}'
    bot.send_message(message.chat.id, message_text)


# FUNCTION FOR 'Support' BUTTOM

@bot.message_handler(func=lambda message: message.text == 'Support')
def handle_help(message):
    global last_command
    last_command = 'help'
    message_text = "If you have troubles or some technical issues contact with us. @vahevyan, @Haykarz"
    bot.send_message(message.chat.id, message_text)


# FUNCTION FOR 'Calculator' BUTTOM

@bot.message_handler(func=lambda message: message.text == 'Calculator')
def handle_calculate(message):
    global calculating, last_command
    calculating = True
    last_command = 'calculator'
    message_text = 'Please enter the amount and crypto to calculate (e.g. 2 BTC):'
    bot.send_message(message.chat.id, message_text)


# FUNCTION FOR 'Graph' BUTTOM

@bot.message_handler(func=lambda message: message.text == 'Graph')
def handle_graph(message):
    global last_command
    last_command = ''

    # Buttoms in 'Graph' menu

    markup = telebot.types.ReplyKeyboardMarkup(row_width=3)
    buttons = [telebot.types.KeyboardButton(crypto) for crypto in cryptos]
    buttons.append(telebot.types.KeyboardButton('Back'))
    markup.add(*buttons)

    # FOR SENDING MESSAGE TO USER FOR CHOOSING CURRENCY

    bot.send_message(message.chat.id, "Which cryptocurrency do you want to plot?", reply_markup=markup)
    bot.register_next_step_handler(message, handle_graph_crypto_input)



# FOR USERS TO INPUT DAYS FOR SHOWING GRAPH

def handle_graph_crypto_input(message):
    if message.text == "Back":
        handle_start(message)
        return
    crypto = message.text.upper()
    bot.send_message(message.chat.id, f"You chose {crypto}. How many days do you want to include in the graph?")
    bot.register_next_step_handler(message, handle_graph_days_input, crypto)


# FUNCTIONAL FOR GRAPH

def handle_graph_days_input(message, crypto):
    try:
        if message.text == 'Back':
            handle_start(message)
            return
        days = int(message.text)
        ticker = yf.Ticker(f"{crypto}-USD")
        start_date = (datetime.today() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = datetime.today().strftime('%Y-%m-%d')
        historical_data = ticker.history(start=start_date, end=end_date)
        plt.figure(figsize=(8, 6))
        plt.plot(historical_data['Close'])
        plt.title(f"{crypto} Price (Last {days} Days)")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.grid(True)
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        bot.send_photo(message.chat.id, photo=buf)

    except ValueError:
        bot.send_message(message.chat.id, "Invalid input. Please enter an integer number of days.")
        bot.register_next_step_handler(message, handle_graph_days_input, crypto)


# FUNCTIONAL FOR CALCULATOR

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global calculating, last_command
    if calculating and last_command == 'calculator':
        try:
            amount, crypto = message.text.split()
            crypto = crypto.upper()
            amount = float(amount)
            if crypto in cryptos:
                rate = get_crypto_rate(crypto)
                value = rate * amount
                message_text = f'{amount:.2f} {crypto} = ${value:.2f}\n'
                bot.send_message(message.chat.id, message_text)
            else:
                bot.send_message(message.chat.id, f'Invalid cryptocurrency. Please choose from {", ".join(cryptos)}')
        except ValueError:
            bot.send_message(message.chat.id, 'Invalid input. Please enter the amount and symbol of cryptocurrency')
    elif message.text == 'Back':
        handle_start(message)
        return
    else:
        last_command = ''
        calculating = False
        bot.send_message(message.chat.id, f'Please use the functions button below first before using the feature.')

# BOT START COMMAND

bot.polling()