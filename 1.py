import html
import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def get_iphone12_guides_list():
    url = "https://www.ifixit.com/api/2.0/wikis/CATEGORY/iPhone%2012?locale=ru"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('guides', [])
    except Exception as e:
        logging.error(f"Ошибка при получении списка: {e}")
        return []


def get_guide_steps(guide_id):
    # ИСПРАВЛЕНО: Правильный путь к эндпоинту инструкций
    url = f"https://www.ifixit.com/api/2.0/guides/{guide_id}?locale=ru"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Ошибка при получении шагов для ID {guide_id}: {e}")
        return None


async def iphone12(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Загружаю список доступных ремонтов...")
    guides = get_iphone12_guides_list()

    if not guides:
        await update.message.reply_text("Инструкции не найдены.")
        return

    keyboard = []
    for guide in guides:
        title = guide.get('title', 'Без названия')
        # ИСПРАВЛЕНО: Поле в API называется guideid
        guide_id = guide.get('guideid')

        if guide_id:
            keyboard.append([InlineKeyboardButton(text=title, callback_data=f"guide_{guide_id}")])

    # Выводим первые 15 инструкций
    reply_markup = InlineKeyboardMarkup(keyboard[:15])
    await update.message.reply_text("Выберите, что именно нужно починить:", reply_markup=reply_markup)


async def handle_guide_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    guide_id = query.data.replace("guide_", "")
    await query.edit_message_text("📥 Загружаю шаги инструкции, подождите...")

    guide_data = get_guide_steps(guide_id)
    if not guide_data:
        await query.message.reply_text("Не удалось загрузить детали инструкции.")
        return

    title = guide_data.get('title', 'Инструкция')
    intro = f"<b>🛠 {html.escape(title)}</b>\n\n"
    await query.message.reply_text(intro, parse_mode='HTML')

    steps_list = guide_data.get('steps', [])

    # ВВОДИМ СВОЙ СЧЕТЧИК, чтобы номера не сбрасывались
    global_step_counter = 1

    for i in range(0, len(steps_list), 3):
        message_text = ""
        chunk = steps_list[i:i + 3]

        for step in chunk:
            # Используем наш счетчик вместо step.get('orderby')
            lines = [line.get('text_raw', '') for line in step.get('lines', [])]
            step_text = " ".join(lines)

            safe_text = html.escape(step_text)
            message_text += f"<b>Шаг {global_step_counter}</b>\n{safe_text}\n\n"

            # Увеличиваем счетчик после каждого шага
            global_step_counter += 1

        image_url = None
        try:
            media = chunk[0].get('media', {}).get('data', [])
            if media:
                image_url = media[0].get('medium') or media[0].get('original')
        except Exception:
            image_url = None

        if image_url:
            await query.message.reply_photo(photo=image_url, caption=message_text[:1024], parse_mode='HTML')
        else:
            await query.message.reply_text(message_text, parse_mode='HTML')
            
if __name__ == '__main__':
    # Вставьте ваш токен здесь
    TOKEN = ""

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("iphone12", iphone12))
    app.add_handler(CallbackQueryHandler(handle_guide_selection, pattern=r"^guide_"))

    print("Бот запущен...")
    app.run_polling()
