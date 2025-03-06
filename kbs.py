from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='View all'), 
    KeyboardButton(text='Configure'),
    KeyboardButton(text='Quit')]
])

config  = ReplyKeyboardMarkup(keyboard=
[
    [KeyboardButton(text='Add a new task'), 
    KeyboardButton(text='Delete your tasks'),
    KeyboardButton(text='Back')]
])

delete = ReplyKeyboardMarkup(keyboard=
[
    [KeyboardButton(text='Delete all'),
    KeyboardButton(text='Delete one task'),
    KeyboardButton(text='Back')]
])