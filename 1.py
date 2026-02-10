import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import asyncio
import random
import time

API_TOKEN = ''  # ← ЗАМЕНИ НА СВОЙ!

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN.strip(), default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Список реальных User-Agents (2026)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

async def scrape_ifixit(query: str):
    """Финальная версия — обходит анти-бот защиту iFixit 2026"""
    search_url = "https://www.ifixit.com/search"
    params = {'q': query}
    url = search_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # === ВАЖНО: Имитация реального пользователя ===
        await page.set_extra_http_headers({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        })

        # === Имитируем поведение человека ===
        await page.goto(url, timeout=15000)

        # Ждём, пока страница загрузится (не просто DOM — а JS-данные)
        await page.wait_for_timeout(3000)  # Ждём 3 секунды

        # Прокручиваем страницу — это "человеческое" поведение
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
        await page.wait_for_timeout(1500)

        # Кликаем на поле поиска (даже если оно не нужно — это "уверенность" бота)
        try:
            await page.locator('input[placeholder="Search for devices, guides, parts"]').click(timeout=2000)
            await page.wait_for_timeout(800)
        except:
            pass  # Не критично

        # Ждём результаты
        await page.wait_for_selector('div[data-testid="search-result"]', timeout=10000)

        # Извлекаем результаты
        items = await page.query_selector_all('div[data-testid="search-result"]')
        results = []

        for item in items[:5]:
            title_el = await item.query_selector('h3.search-result-title')
            link_el = await item.query_selector('a')
            img_el = await item.query_selector('img')

            if not title_el or not link_el:
                continue

            title = await title_el.text_content()
            href = await link_el.get_attribute('href')
            img_src = await img_el.get_attribute('src') if img_el else None

            if not title or not href:
                continue

            url_full = urljoin("https://www.ifixit.com", href)
            results.append({
                'title': title.strip(),
                'url': url_full,
                'image': img_src
            })

        await browser.close()
        return results

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🔧 **Прямой поиск по iFixit активен.**\nНапиши модель устройства (на английском).")

@dp.message()
async def search_handler(message: types.Message):
    query = message.text.strip()
    if len(query) < 2:
        return

    status_msg = await message.answer(f"🔎 Ищу `{query}`...")

    guides = await scrape_ifixit(query)
    await status_msg.delete()

    if not guides:
        await message.answer("❌ Ничего не найдено. Попробуй: *iPhone 13 battery*, *Samsung S23 screen*")
        return

    for guide in guides:
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="📖 Инструкция", url=guide['url']))

        text = f"🛠 **{guide['title']}**"
        if guide['image']:
            try:
                await message.answer_photo(photo=guide['image'], caption=text, reply_markup=builder.as_markup())
            except Exception as e:
                logging.warning(f"Не удалось отправить фото: {e}")
                await message.answer(text=text, reply_markup=builder.as_markup())
        else:
            await message.answer(text=text, reply_markup=builder.as_markup())

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))

