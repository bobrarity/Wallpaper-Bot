from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def generate_categories(categories):
    markup = ReplyKeyboardMarkup(row_width=3)
    buttons = []
    for category in categories:
        btn = KeyboardButton(text=category[0])
        buttons.append(btn)
    markup.add(*buttons)
    return markup



def generate_download_button(image_id):
    markup = InlineKeyboardMarkup()
    dwn = InlineKeyboardButton(text='Download the image', callback_data=f'download_{image_id}')
    markup.add(dwn)
    return markup