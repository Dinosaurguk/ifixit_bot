<p align="center">
<img width="894" height="352" alt="изображение" src="https://github.com/user-attachments/assets/9c480890-a7ef-4e7d-b902-bae3b2b40db3">
</p>

<p align="center">
  <a href="https://github.com/[ТВОЙ_ЛОГИН]/[ИМЯ_РЕПО]/releases">
    <img src="https://img.shields.io/badge/Version-v1.0.0-brightgreen.svg?style=flat-square" alt="Latest Version" />
  </a>
  <a href="https://github.com/[ТВОЙ_ЛОГИН]/[ИМЯ_РЕПО]/actions">
    <img src="https://img.shields.io/badge/Build-passing-brightgreen.svg?style=flat-square" alt="Build Status" />
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square" alt="Python Version" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License" />
  </a>
  <a href="https://github.com/[[Логин](https://github.com/Dinosaurguk)]">
    <img src="https://img.shields.io/badge/Author-[Студент - Dinosauriguk]-orange.svg?style=flat-square" alt="Author" />
  </a>
  <a href="https://t.me/[ifixit_bot]">
    <img src="https://img.shields.io/badge/Telegram-Bot-blue.svg?style=flat-square" alt="Telegram Bot" />
  </a>
</p>

<p align="center">
  <a href="README.md">
    <b>Русское описание</b>
</p>

# iFixit Repair Telegram Bot
<h1 align="left">
   Telegram бот для поиска инструкций по ремонту техники

## Architectural
</h1>
<p align="center">
  <img width="1679" height="792" alt="изображение" src="https://github.com/user-attachments/assets/c3a83068-40b2-4ee1-84a8-6703e7c69264" />
>
</p>

## Usage
1. Запуск поиска: Введи команду /repair и через пробел название гаджета.
        Пример: /repair iPhone 17 или /repair PlayStation.
2. Уточнение: Бот выкатит список похожих устройств. Нажми на кнопку с нужной моделью.
3. Выбор поломки: Выбери, что именно пошло не так (например, «Замена аккумулятора» или «Разборка»).
4. Ремонт: Бот пришлет ссылку или пошаговый гайд. Открывай и следуй инструкциям, глядя на картинки.

Если забудешь, что искал вчера, команда /history покажет последние запросы.

## Installation

1. **Клонируй репозиторий:**
   ```bash
   git clone https://github.com/Dinosaurguk/ifixit_bot/blob/main/1.py
   cd ifixit-repair-bot

## Useful Links
* https://ru.ifixit.com/ - сам сайт ifixit
* https://ru.ifixit.com/api/2.0/doc/ - API документация


## Functionality & Libraries
1. [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) — Основной фреймворк для реализации логики бота и обработки команд.
2. [requests](https://github.com/psf/requests) — Работа с iFixit API 2.0 для получения данных о категориях и шагах ремонта.
3. [sqlite3](https://docs.python.org/3/library/sqlite3.html) — Локальное хранение истории поисковых запросов пользователей.
4. [urllib.parse](https://docs.python.org/3/library/urllib.parse.html) — Формирование корректных URL-запросов к базе данных iFixit.
5. [html](https://docs.python.org/3/library/html.html) — Безопасное отображение текста инструкций в интерфейсе Telegram.

## Acknowledgments & Mission
Огромная благодарность команде [iFixit](https://www.ifixit.com) за их открытый [API](https://www.ifixit.com/api/2.0/doc) и приверженность философии **Right to Repair** (Право на ремонт). 
