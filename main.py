from aiogram import executor, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from random import randint
import os
from dotenv import load_dotenv
import sqlite3
from keyboards import generate_categories, generate_download_button
import re
load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    await message.answer('Welcome! Here you will find wallpapers for all tastes!')
    await show_categories(message)


async def show_categories(message: Message):
    chat_id = message.chat.id
    database = sqlite3.connect('wallpapers.db')
    cursor = database.cursor()

    cursor.execute('''
    SELECT category_name FROM categories;
    ''')
    categories = cursor.fetchall()
    database.close()
    await message.answer('Choose a category: ', reply_markup=generate_categories(categories))



@dp.message_handler(content_types=['text'])
async def get_image_by_category(message: Message):
    database = sqlite3.connect('wallpapers.db')
    cursor = database.cursor()

    category_name = message.text

    cursor.execute('''
    SELECT category_id FROM categories WHERE category_name = ?
    ''', (category_name, ))
    category_id = cursor.fetchone()

    if category_id:
        cursor.execute('''
        SELECT image_link FROM images WHERE category_id = ?
        ''', (category_id[0], ))
        image_links = cursor.fetchall()
        random_index = randint(0, len(image_links) - 1)
        random_image_link = image_links[random_index]

        resolution = re.search(r'[0-9]+x[0-9]+', random_image_link[0])[0]


        cursor.execute('''
        SELECT image_id FROM images WHERE image_link = ?
        
        ''', (random_image_link[0], ))
        image_id = cursor.fetchone()[0]


        try:
            await message.answer_photo(photo=random_image_link[0],
                                       caption=f'Resolution: {resolution}',
                                       reply_markup=generate_download_button(image_id))

        except:
            resize_link = random_image_link[0].replace(resolution, '1920x1080')
            await message.answer_photo(photo=resize_link,
                                       caption=f'Resolution: {resolution} was changed',
                                       reply_markup=generate_download_button(image_id))

    else:
        await message.answer('Please select from the categories below: ')
        await show_categories(message)
    database.close()

@dp.callback_query_handler(lambda call: 'download' in call.data)
async def download_function(call: CallbackQuery):
    _, image_id = call.data.split('_')
    database = sqlite3.connect('wallpapers.db')
    cursor = database.cursor()

    cursor.execute('''
    SELECT image_link FROM images WHERE image_id = ?
    ''', (int(image_id), ))
    image_link = cursor.fetchone()[0]
    chat_id = call.message.chat.id
    database.close()
    await bot.send_document(chat_id, image_link)

executor.start_polling(dp)

