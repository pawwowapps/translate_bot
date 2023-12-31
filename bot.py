from dotenv import load_dotenv
import telebot
import os
from googletrans import Translator
from json_translator import translateJson
from xml_translator import translateXml
import zipfile
import sys
load_dotenv()

debug = os.getenv("DEBUG")
# telegram_token = os.getenv("TELEGRAM_TOKEN_DEBUG") if debug else os.getenv("TELEGRAM_TOKEN")
telegram_token = '6953404835:AAGh27UXqujVsvAixAZV7zuWBUwAU4n9p44'
user_token = os.getenv("USER_TOKEN")

bot = telebot.TeleBot(token=telegram_token)
URL = 'https://translate-bot-7jy3.onrender.com'  # Replace with your Render.com app URL


# Define a function to handle file messages
@bot.message_handler(content_types=['document'])
def handle_file(message):
    file_id = message.document.file_id
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_info.file_path}"

    # Download the file
    file_extension = file_info.file_path.split('.')[-1]
    downloaded_file_path = f"downloaded_file.{file_extension}"
    os.system(f"curl -o {downloaded_file_path} {file_url}")

    # Send the downloaded file back to the user
    with open(downloaded_file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)


translator = Translator()

# Створення клавіатури для вибору мови
language_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
language_keyboard.row('Англійська', 'Іспанська', 'Французька')
language_keyboard.row('Німецька', 'Італійська', 'Індонезійська')
language_keyboard.row('Польська', 'Португальська', 'Старт')

# Словник для відображення кодів мови
language_codes = {
    'Англійська': 'en',
    'Іспанська': 'es',
    'Французька': 'fr',
    'Німецька': 'de',
    'Італійська': 'it',
    'Індонезійська': 'id',
    'Польська': 'uk',
    'Португальська': 'pt',
}

# Обробник для команди /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Хельо! Вибери мови для перекладу файлу:", reply_markup=language_keyboard)
    bot.register_next_step_handler(message, handle_language_selection)

def handle_language_selection(message):
    chat_id = message.chat.id
    selected_language = message.text

    if selected_language == 'Старт':
        handle_start(message)
        return

    if selected_language == 'Інша':
        bot.send_message(chat_id, "Будь ласка, введіть код мови (наприклад, 'ja' для японської).")
        bot.register_next_step_handler(message, handle_custom_language)
        return

    # if selected_language not in language_codes:
    #     bot.send_message(chat_id, "Будь ласка, вибери коректну мову зі списку.")
    #     return

    bot.send_message(chat_id, "Тепер дай мені файл для перекладу.")
    bot.register_next_step_handler(message, handle_translation, selected_language)

def handle_custom_language(message):
    chat_id = message.chat.id
    selected_language = message.text

    if selected_language.strip() == '':
        bot.send_message(chat_id, "Будь ласка, введи код мови.")
        bot.register_next_step_handler(message, handle_custom_language)
        return

    bot.send_message(chat_id, "Тепер дай мені файл для перекладу.")
    bot.register_next_step_handler(message, handle_translation, selected_language)

def handle_translation(message, selected_language):
    if message.content_type == 'document':
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_extension = file_info.file_path.split('.')[-1]
        file_name = message.document.file_name.split('.')[0]
        languages_to_translate = selected_language.split(",")
        if 'json' in file_extension:
            bot.send_message(message.chat.id, f"Перекладаю на: {selected_language}.")
            for language_name in languages_to_translate:
                lang = language_name.strip()
                file_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_info.file_path}"
                target_language = language_codes.get(lang, lang)
                # Download the file
                downloaded_file_path = f"{file_name}_{target_language}.{file_extension}"
                os.system(f"curl -o {downloaded_file_path} {file_url}")
                translateJson(downloaded_file_path, target_language)

                with open(downloaded_file_path, 'rb') as file:
                    bot.send_document(message.chat.id, file)
                    handle_start(message)
        elif 'xml' in file_extension:
            bot.send_message(message.chat.id, f"Перекладаю на: {selected_language}.")
            folder_names = []
            for language_name in languages_to_translate:
                lang = language_name.strip()
                file_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_info.file_path}"
                target_language = language_codes.get(lang, lang)
                # Download the file
                os.makedirs(f"values-{target_language}", exist_ok=True)
                downloaded_file_path = f"values-{target_language}/{file_name}.{file_extension}"
                os.system(f"curl -o {downloaded_file_path} {file_url}")
                translateXml(downloaded_file_path, target_language)

                folder_names.append(f"values-{target_language}")
            zip_filename = 'archive.zip'
            with zipfile.ZipFile(zip_filename, 'w') as zip_file:
                for folder_name in folder_names:
                    for root, dirs, files in os.walk(folder_name):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, folder_name)
                            zip_file.write(file_path, os.path.join(folder_name, arcname))

            with open(zip_filename, 'rb') as zip_file:
                bot.send_document(message.chat.id, zip_file)

            os.remove(zip_filename)


if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=URL)
    # bot.infinity_polling(none_stop=True)

