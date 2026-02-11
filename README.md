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
  <a href="https://github.com/[ТВОЙ_ЛОГИН]">
    <img src="https://img.shields.io/badge/Author-[dinosaurguk]-orange.svg?style=flat-square" alt="Author" />
  </a>
  <a href="https://t.me/[ИМЯ_ТВОЕГО_БОТА]">
    <img src="https://img.shields.io/badge/Telegram-Bot-blue.svg?style=flat-square" alt="Telegram Bot" />
  </a>
</p>

<p align="center">
  <a href="README_EN.md">
    <b>English Version 🌐</b>
  </a>
</p>

## iFixit Repair Telegram Bot

<h1 align="left">
   Telegram-бот для поиска инструкций по ремонту техники
</h1>

Этот проект родился из интереса к теме самостоятельного ремонта. В процессе разработки я столкнулся с тем, что создание качественной архитектуры — это настоящий вызов. Бывали моменты, когда хотелось все переделать с нуля из-за ошибок в самой базе кода, но именно этот опыт помог мне лучше понять принципы работы с API и данными. Это мой путь проб и ошибок, который привел к рабочему результату. Надеюсь на вашу поддержку и высокую оценку! :)

## Схема архитектуры
<p align="center">
  <img width="1679" height="792" alt="Architecture Diagram" src="https://github.com/user-attachments/assets/c3a83068-40b2-4ee1-84a8-6703e7c69264" />
</p>

## Использование
1. **Запуск поиска:** Введите команду `/repair` и через пробел название устройства.
   *Пример: `/repair iPhone 17` или `/repair PlayStation`.*
2. **Уточнение:** Бот предложит список подходящих моделей. Выберите нужную.
3. **Выбор поломки:** Выберите тип ремонта (например, «Замена аккумулятора» или «Разборка»).
4. **Ремонт:** Бот пришлет ссылку или пошаговое руководство. Следуйте инструкциям и иллюстрациям.

*Команда `/history` покажет ваши последние запросы.*

## Установка
1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/Dinosaurguk/ifixit_bot.git

## Полезные ссылки

* https://ru.ifixit.com/ - сам сайт ifixit
* https://ru.ifixit.com/api/2.0/doc/ - API документация

## Функционал и библиотеки

1. [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
2. [requests](https://github.com/psf/requests)
3. [sqlite3](https://docs.python.org/3/library/sqlite3.html) 
4. [urllib.parse](https://docs.python.org/3/library/urllib.parse.html) 
5. [html](https://docs.python.org/3/library/html.html) 

## Благодарности и миссия

Огромная благодарность команде [iFixit](https://www.ifixit.com) за их открытый [API](https://www.ifixit.com/api/2.0/doc) и приверженность философии **Right to Repair** (Право на ремонт). 

##Лицензия
Этот проект распространяется под лицензией MIT. Подробнее см. в файле [LICENSE](LICENSE).
