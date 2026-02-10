import html
import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

def get_all_iphone12_guides_ru():
    url = "https://www.ifixit.com/api/2.0/wikis/CATEGORY/iPhone%2012?locale=ru"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('guides', [])
    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        return []

async def iphone12(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🇷🇺 Загружаю полный список инструкций...")

    guides = get_all_iphone12_guides_ru()

    if not guides:
        await update.message.reply_text("Инструкции не найдены.")
        return

    full_message = "<b>🛠 ВСЕ варианты ремонта iPhone 12:</b>\n\n"

    for guide in guides:
        title = html.escape(guide.get('title', 'Без названия'))
        raw_url = guide.get('url', '').strip()

        if raw_url:
            if not raw_url.startswith('http'):
                clean_url = f"https://ru.ifixit.com{raw_url if raw_url.startswith('/') else '/' + raw_url}"
            else:
                clean_url = raw_url.replace("www.ifixit.com", "ru.ifixit.com")

            # Используем двойные кавычки для атрибута href
            line = f"▪️ {title}\n🔗 <a href=\"{clean_url}\">Инструкция на русском</a>\n\n"
        else:
            line = f"▪️ {title} (Ссылка недоступна)\n\n"

        if len(full_message) + len(line) > 3800:
            try:
                await update.message.reply_text(full_message, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                logging.error(f"Ошибка при отправке части сообщения: {e}")
                await update.message.reply_text("Ошибка в оформлении части списка, пропускаю её...")
            full_message = ""

        full_message += line

    if full_message.strip():
        try:
            await update.message.reply_text(full_message, parse_mode='HTML', disable_web_page_preview=True)
        except Exception as e:
            logging.error(f"Final message error: {e}")
            await update.message.reply_text("Произошла ошибка при выводе списка. Попробуйте позже.")

if __name__ == '__main__':
    # Вставь сюда свой токен
    TOKEN = ''

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('iphone12', iphone12))
    print("Бот запущен...")
    application.run_polling()
