# bot.py
import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# ВСТАВЬ СЮДА СВОЙ ТОКЕН ОТ @BOTFATHER
API_TOKEN = ""  # ЗАМЕНИ ЭТУ СТРОКУ НА СВОЙ ТОКЕН!

# Ключ для iFixit API (публичный демо-ключ)
IFIXIT_API_KEY = "e1iy329yt1o8723t"

# Проверка токена
if not API_TOKEN or API_TOKEN == "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz":
    print("ОШИБКА: Вставь свой токен от @BotFather!")
    exit(1)

print("Бот запускается...")

IFIXIT_API_URL = "https://www.ifixit.com/api/2.0"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Временное хранилище данных пользователей
user_sessions = {}

# Заголовки для запросов
HEADERS = {
    'User-Agent': 'TelegramRepairBot/1.0'
}


# Функция для запросов к публичному API iFixit
async def make_ifixit_request(endpoint: str, params: dict = None):
    if params is None:
        params = {}

    # Добавляем API ключ к параметрам
    params['key'] = IFIXIT_API_KEY

    url = f"{IFIXIT_API_URL}/{endpoint}"

    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Ошибка API: {response.status}")
                    return None
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return None


# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    welcome_text = """
🔧 *Привет! Я бот-помощник по ремонту на основе iFixit*

Введи название устройства, которое хочешь починить:
• iPhone 13
• MacBook Pro 2020  
• PlayStation 5
• Или любое другое устройство

_Пример: «samsung galaxy s20»_
    """
    await message.answer(welcome_text, parse_mode='Markdown')


# Поиск устройств
@dp.message(F.text & ~F.text.startswith('/'))
async def handle_search(message: types.Message):
    search_query = message.text.strip()

    if len(search_query) < 2:
        await message.answer("Введите более конкретный запрос (минимум 2 символа)")
        return

    await message.answer("🔍 Ищу устройства...")

    # Поиск через публичное API iFixit
    search_data = await make_ifixit_request("search", {'query': search_query})

    if not search_data or not search_data.get('results'):
        await message.answer("❌ Устройств не найдено. Попробуйте другой запрос.")
        return

    # Создаем кнопки с найденными устройствами
    keyboard = []
    for device in search_data['results'][:8]:  # Берем первые 8 результатов
        # Более безопасное извлечение названия устройства
        device_name = device.get('title', 'Неизвестное устройство')
        device_id = device.get('docid')

        if device_id and device_name:
            # Обрезаем длинные названия
            display_name = device_name[:40] + "..." if len(device_name) > 40 else device_name
            keyboard.append([
                types.InlineKeyboardButton(
                    text=f"📱 {display_name}",
                    callback_data=f"device_{device_id}"
                )
            ])

    if not keyboard:  # Если нет подходящих результатов
        await message.answer("❌ Устройств не найдено. Попробуйте другой запрос.")
        return

    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("📱 Выберите устройство:", reply_markup=reply_markup)


# Показ гайдов для выбранного устройства
@dp.callback_query(F.data.startswith("device_"))
async def show_guides(callback: types.CallbackQuery):
    device_id = callback.data.split('_')[1]

    await callback.message.edit_text("📖 Загружаю руководства...")

    # Получаем гайды для устройства
    guides_data = await make_ifixit_request("guides", {'device': device_id})

    if not guides_data:
        await callback.message.edit_text("❌ Руководства не найдены.")
        return
# Создаем кнопки с гайдами
    keyboard = []
    for guide in guides_data[:10]:  # Берем первые 10 гайдов
        title = guide.get('title', 'Без названия')
        guide_id = guide.get('guideid')

        if guide_id and title:
            display_title = title[:35] + "..." if len(title) > 35 else title
            keyboard.append([
                types.InlineKeyboardButton(
                    text=f"🔧 {display_title}",
                    callback_data=f"guide_{guide_id}"
                )
            ])

    if not keyboard:  # Если нет гайдов
        await callback.message.edit_text("❌ Руководства не найдены.")
        return

    # Кнопка "Назад" к поиску
    keyboard.append([
        types.InlineKeyboardButton(text="⬅️ Назад к поиску", callback_data="back_to_search")
    ])

    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    await callback.message.edit_text("📚 Доступные руководства:", reply_markup=reply_markup)
    await callback.answer()


# Показ конкретного гайда
@dp.callback_query(F.data.startswith("guide_"))
async def show_guide(callback: types.CallbackQuery):
    guide_id = callback.data.split('_')[1]

    await callback.message.edit_text("🔄 Загружаю руководство...")

    # Получаем полную информацию о гайде
    guide_data = await make_ifixit_request(f"guide/{guide_id}")

    if not guide_data or 'steps' not in guide_data:
        await callback.message.edit_text("❌ Ошибка загрузки руководства.")
        return

    # Сохраняем данные гайда для пользователя
    user_sessions[callback.from_user.id] = {
        'guide_data': guide_data,
        'current_step': 0,
        'total_steps': len(guide_data['steps'])
    }

    # Показываем первый шаг
    await show_guide_step(callback.message, callback.from_user.id, 0)
    await callback.answer()


# Функция показа шага гайда
async def show_guide_step(message: types.Message, user_id: int, step_index: int):
    if user_id not in user_sessions:
        await message.answer("❌ Сессия устарела. Начните поиск заново.")
        return

    guide_data = user_sessions[user_id]['guide_data']
    steps = guide_data['steps']

    if step_index < 0 or step_index >= len(steps):
        await message.answer("🏁 Руководство завершено!")
        return

    # Обновляем текущий шаг
    user_sessions[user_id]['current_step'] = step_index

    step = steps[step_index]

    # Извлекаем текст шага
    step_text = "Описание отсутствует"
    if step.get('lines') and len(step['lines']) > 0:
        step_text = step['lines'][0].get('text', 'Описание отсутствует')

    # Формируем текст шага
    caption = f"*Шаг {step_index + 1}/{len(steps)}*\n\n{step_text}"

    # Получаем URL изображения (если есть)
    image_url = None
    if step.get('media') and step['media'].get('image'):
        image_url = step['media']['image'].get('large')

    # Создаем клавиатуру навигации
    keyboard_buttons = []

    if step_index > 0:
        keyboard_buttons.append(
            types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"step_{step_index - 1}")
        )

    if step_index < len(steps) - 1:
        keyboard_buttons.append(
            types.InlineKeyboardButton(text="Вперед ➡️", callback_data=f"step_{step_index + 1}")
        )

    # Кнопка "Назад к гайдам"
    keyboard_buttons.append(
        types.InlineKeyboardButton(text="📚 К списку гайдов", callback_data="back_to_guides")
    )

    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=[keyboard_buttons])

    # Отправляем сообщение с изображением или без
    if image_url:
        await message.answer_photo(
            photo=image_url,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await message.answer(
            caption,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
# Обработка навигации по шагам
@dp.callback_query(F.data.startswith("step_"))
async def handle_step_navigation(callback: types.CallbackQuery):
    step_index = int(callback.data.split('_')[1])
    user_id = callback.from_user.id

    if user_id not in user_sessions:
        await callback.answer("Сессия устарела")
        return

    await show_guide_step(callback.message, user_id, step_index)
    await callback.answer()


# Назад к списку гайдов
@dp.callback_query(F.data == "back_to_guides")
async def back_to_guides(callback: types.CallbackQuery):
    if callback.from_user.id in user_sessions:
        del user_sessions[callback.from_user.id]

    await callback.message.edit_text("Введите название устройства для нового поиска:")
    await callback.answer()


# Назад к поиску
@dp.callback_query(F.data == "back_to_search")
async def back_to_search(callback: types.CallbackQuery):
    if callback.from_user.id in user_sessions:
        del user_sessions[callback.from_user.id]

    await callback.message.edit_text("Введите название устройства для поиска:")
    await callback.answer()


# Запуск бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if name == "main":
    import asyncio

    asyncio.run(main())