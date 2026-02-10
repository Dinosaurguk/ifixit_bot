<p align="center">
<img width="894" height="352" alt="изображение" src="https://github.com/user-attachments/assets/9c480890-a7ef-4e7d-b902-bae3b2b40db3">
>
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

## Useful Links
* https://ru.ifixit.com/ - сам сайт ifixit
* https://ru.ifixit.com/api/2.0/doc/ - API документация


## Functionality & Libraries
1. [requests](https://github.com/psf/requests)
2. [urllib.parse](https://docs.python.org/3/library/urllib.parse.html)
3. [html](https://docs.python.org/3/library/html.html)
4. [squlite3](https://docs.python.org/3/library/sqlite3.html)
5. [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

## Acknowledgments
Особая благодарность команде [iFixit](https://www.ifixit.com) за их открытый [API](https://www.ifixit.com/api/2.0/doc), который позволяет разработчикам свободно использовать крупнейшую в мире базу знаний по ремонту. Этот проект создан с целью сделать инструкции по самостоятельному ремонту еще доступнее.
