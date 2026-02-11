import html
import requests
import urllib.parse
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Настройки (settingi vsyakie)
ITEMS_PER_PAGE = 10
DB_NAME = 'ifixit_bot.db'


# БД (/history)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def save_search(user_id, query):
    conn = sqlite3.connect(DB_NAME)
    conn.cursor().execute('INSERT INTO search_history (user_id, query) VALUES (?, ?)', (user_id, query))
    conn.commit()
    conn.close()


def get_history(user_id):
    conn = sqlite3.connect(DB_NAME)
    rows = conn.cursor().execute('''
        SELECT query, timestamp FROM search_history 
        WHERE user_id = ? 
        ORDER BY timestamp DESC LIMIT 10
    ''', (user_id,)).fetchall()
    conn.close()
    return rows


# Апишка
def search_ifixit_categories(query):
    encoded = urllib.parse.quote(query)
    url = f"https://www.ifixit.com/api/2.0/search/{encoded}?type=category&locale=ru"

    # мусорные кнопочки клак клак, да врятли или врядли я не русский кто то это будет читать лялялляляляляля
    JUNK = [
        'accessories', 'tools', 'screen', 'display', 'battery', 'adhesive',
        'kit', 'case', 'cable', 'charger', 'glass', 'bundle', 'turn', 'issues',
        'keeps', 'button', 'buttons', 'kernel', 'panic', 'On', 'Off', 'charging',
        'speaker', 'shuts', 'quality', 'chip', 'Teardown', 'How', 'id', 'signal',
        'parts', 'camera', 'port', 'flex', 'board', 'housing', 'cover', 'mic','sensor',
        'digitizer', 'lcd', 'panel', 'toolkit', 'screwdriver', 'sound', 'timer',
        'spudger', 'driver', 'bit', 'boot', 'loop', 'frozen', 'slow', 'broken',
        'cracked', 'not working', 'fix', 'repair', 'restarting', 'problem', 'error',
        'failure', 'band', 'stand', 'apparel', 'merch', 'box', 'teardown', 'batteries',
        'review', 'how to', 'faq', 'troubleshooting', 'guide', 'manual', 'stuck',
        'instructions', 'freezing', 'TV', 'picture', 'image', 'beeping', 'power',

    ]

    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200: return []
        data = res.json().get('results', [])
        return [i for i in data if
                not any(w in i.get('title', '').lower() for w in JUNK) and len(i.get('title', '')) < 35]
    except:
        return []

# куколдит и ищет сначало русское
def get_category_content(cat_name):
    encoded = urllib.parse.quote(cat_name)
    url = f"https://www.ifixit.com/api/2.0/wikis/CATEGORY/{encoded}?locale=ru"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200: return None
        data = res.json()
        guides = [g for g in data.get('guides', []) if "teardown" not in g.get('title', '').lower()]
        if guides: return {"type": "guides", "items": guides}
        #Поиск во внутренностях
        if data.get('children'):
            kids = []
            for c in data['children']:
                if not any(w in c.get('title', '').lower() for w in ['parts', 'accessories', 'запчасти']):
                    kids.append({"title": c.get('title')})
            if kids: return {"type": "categories", "items": kids}
    except:
        pass
    return None


def get_guide_steps(gid):
    try:
        return requests.get(f"https://www.ifixit.com/api/2.0/guides/{gid}?locale=ru", timeout=10).json()
    except:
        return None


# Кнопки
def build_kb(items, page, prefix):
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    batch = items[start:end]
    buttons = []
    for i, item in enumerate(batch):
        callback = f"cat_idx_{start + i}" if prefix == "cat" else f"guide_{item.get('guideid')}"
        buttons.append([InlineKeyboardButton(text=item.get('title', '???')[:50], callback_data=callback)])

    nav = []
    if page > 0: nav.append(InlineKeyboardButton("⬅️", callback_data=f"page_{prefix}_{page - 1}"))
    if end < len(items): nav.append(InlineKeyboardButton("➡️", callback_data=f"page_{prefix}_{page + 1}"))
    if nav: buttons.append(nav)
    if prefix == "guide":
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_models")])
    return InlineKeyboardMarkup(buttons)


# /Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "<b>Бот для поиска инструкций по ремонту</b>\n\n"
        "Привет! Я помогу найти подробные инструкции по ремонту твоей техники с помощью базы знаний iFixit. "
        "Популярные штуки нахожу быстро, с редкими — как повезет (база постоянно обновляется). Ищу сначала на русском, "
        "если нет — выдам оригинал.\n\n"
        "<b>Команды:</b>\n"
        "<b>/repair [модель]</b> — поиск (можно не полностью)\n"
        "<b>/history</b> — что ты искал раньше\n\n"
        "<b>Как юзать:</b>\n"
        "1. Пишешь /repair + модель\n"
        "2. Выбираешь устройство из списка\n"
        "3. Тыкаешь в свою проблему\n"
        "4. Смотришь шаги с картинками\n\n"
        "Чинить тумбочки не умеет!!! только техника."
    )
    await update.message.reply_text(msg, parse_mode='HTML')


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_history(update.effective_user.id)
    if not rows:
        await update.message.reply_text("История пуста.")
        return
    out = "<b>Последние запросы:</b>\n\n"
    for i, (q, t) in enumerate(rows, 1):
        out += f"{i}. <code>{q}</code> ({t.split('.')[0]})\n"
    await update.message.reply_text(out, parse_mode='HTML')


async def repair_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Пример: /repair iPhone 12")
        return
    save_search(update.effective_user.id, query)
    await update.message.reply_text(f"Ищу: {query}...")
    res = search_ifixit_categories(query)
    if not res:
        await update.message.reply_text("Ничего не нашел :(")
        return
    context.user_data['found_cats'] = res
    await update.message.reply_text("Выбери модель:", reply_markup=build_kb(res, 0, "cat"))


# отмотки
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "back_to_models":
        cats = context.user_data.get('found_cats', [])
        if cats: await query.edit_message_text("Выбери модель:", reply_markup=build_kb(cats, 0, "cat"))
        return

    if data == "back_to_guides":
        guides = context.user_data.get('current_guides', [])
        name = context.user_data.get('current_cat_name', 'устройства')
        if guides: await query.edit_message_text(f"Что в {name} сломалось?", reply_markup=build_kb(guides, 0, "guide"))
        return

    if data.startswith("page_"):
        _, pref, p = data.split("_")
        items = context.user_data.get('found_cats' if pref == "cat" else 'current_guides', [])
        if items: await query.edit_message_reply_markup(reply_markup=build_kb(items, int(p), pref))
        return

    if data.startswith("cat_idx_"):
        idx = int(data.replace("cat_idx_", ""))
        cat = context.user_data['found_cats'][idx].get('title')
        context.user_data['current_cat_name'] = cat
        await query.edit_message_text(f"Гружу {cat}...")
        content = get_category_content(cat)
        if not content:
            await query.edit_message_text("Тут пусто.", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️", callback_data="back_to_models")]]))
            return
        if content['type'] == "guides":
            context.user_data['current_guides'] = content['items']
            await query.edit_message_text(f"Что в {cat} сломалось?",
                                          reply_markup=build_kb(content['items'], 0, "guide"))
        else:
            context.user_data['found_cats'] = content['items']
            await query.edit_message_text(f"Выбери версию {cat}:", reply_markup=build_kb(content['items'], 0, "cat"))

    elif data.startswith("guide_"):
        gid = data.replace("guide_", "")
        wait = await query.message.reply_text("Загрузка...")
        gdata = get_guide_steps(gid)
        if not gdata:
            await wait.edit_text("Ошибка загрузки.")
            return

        url = gdata.get('url', '')
        site = f"https://ru.ifixit.com{url}" if not url.startswith('http') else url.replace("www.ifixit.com",
                                                                                            "ru.ifixit.com")
        await query.message.reply_text(
            f"<b>🛠 {html.escape(gdata.get('title', ''))}</b>\n\nВремя: {gdata.get('time_required')}",
            parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 На сайт", url=site)]]))

        steps = gdata.get('steps', [])
        for i in range(0, len(steps), 3):
            txt = ""
            chunk = steps[i:i + 3]
            for idx, s in enumerate(chunk, start=i + 1):
                lines = [l.get('text_raw', '') for l in s.get('lines', [])]
                txt += f"<b>Шаг {idx}</b>\n{html.escape(' '.join(lines))}\n\n"

            img = None
            try:
                m = chunk[0].get('media', {}).get('data', [])
                if m: img = m[0].get('medium')
            except:
                pass

            if img:
                try:
                    await query.message.reply_photo(photo=img, caption=txt[:1024], parse_mode='HTML')
                except:
                    await query.message.reply_text(txt, parse_mode='HTML')
            else:
                await query.message.reply_text(txt, parse_mode='HTML')

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Назад к списку поломок", callback_data="back_to_guides")],
            [InlineKeyboardButton("(╯°□°）╯︵ ┻━┻ На главную (последний запрос)", callback_data="back_to_models")]
        ])
        await query.message.reply_text("Готово! Можно вернуться назад:", reply_markup=kb)
        await wait.delete()


if __name__ == '__main__':
    init_db()
    TOKEN = ""
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("repair", repair_search))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()

