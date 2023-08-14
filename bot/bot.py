import os
import asyncio
from selenium import webdriver
import bs4
import lxml
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode

API_TOKEN = '6318770206:AAHSybvbf5iSlnO1yQjo8v2iIGYRuVFWVME'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

async def async_start_parser(chat_id, url, target_price):
    driver = webdriver.Chrome()
    driver.get(url)

    while True:
        page_content = driver.page_source
        soup = bs4.BeautifulSoup(page_content, 'lxml')

        order_rows = soup.find_all('div', class_='row order-row--Alcph')

        for order_row in order_rows:
            order_type_elem = order_row.find('div', class_='order-type-marker--cHJF6')
            username_elem = order_row.find('span', class_='user__name--xF_ju')
            user_status_elem = order_row.find('span', class_='ingame--OWe2B')
            reputation_elem = order_row.find('div', class_='user__reputation user__reputation--neutral')
            price_elem = order_row.find('b', class_='price')

            if all(elem is not None for elem in [order_type_elem, username_elem, user_status_elem, reputation_elem, price_elem]):
                order_type = order_type_elem.text
                username = username_elem.text
                user_status = user_status_elem.text
                reputation = reputation_elem.text
                price = price_elem.text

                if price == target_price:
                    message_text = (
                        f"Found target price: {price}\n"
                        f"Order Type: {order_type}\n"
                        f"Username: {username}\n"
                        f"User Status: {user_status}\n"
                        f"Reputation: {reputation}\n"
                        f"Price: {price}"
                    )

                    await bot.send_message(chat_id, message_text, parse_mode=ParseMode.MARKDOWN)
                    driver.quit()
                    return

        await asyncio.sleep(5)
        driver.refresh()


@dp.message_handler(commands=['wait'])
async def start_waiting(message: types.Message):
    chat_id = message.chat.id

    try:
        _, url, target_price = message.text.split()
        target_price = target_price.strip()
        await message.reply(f"Waiting for target price {target_price} on {url}...")

        loop = asyncio.get_event_loop()
        loop.create_task(async_start_parser(chat_id, url, target_price))
    except ValueError:
        await message.reply("Invalid command format. Use /wait URL target_price")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
