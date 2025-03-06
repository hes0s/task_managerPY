import os 
import logging 
from datetime import datetime
from aiogram import Bot, Dispatcher,F
from aiogram.types import Message
from dotenv import load_dotenv
import asyncio
from aiogram.fsm.state import State, StatesGroup
import kbs
from db import conn, cursor 
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, \
    get_user_locale




class Add(StatesGroup ):
    tname = State()
    tdescription = State()
    tdate = State()

class delete(StatesGroup):
    dname = State()

load_dotenv()

## setting up bot vars
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(F.text == "/start")
async def process_start_command(message: Message):
    await message.reply("Hi! I'm your task manager", reply_markup=kbs.main)

@dp.message(F.text == "Configure")
async def configure(message: Message):
    await message.reply("Choose an option:", reply_markup=kbs.config)

#FSM states
@dp.message(F.text == "Add a new task")
async def add_task(message: Message, state: Add):
    await message.answer("You entered adding mode. Please follow the instructions.")
    await state.set_state(Add.tname)
    await message.answer("Enter name: ")

@dp.message(Add.tname)
async def description(message:Message, state: Add):
    await state.update_data(tname=message.text)
    await state.set_state(Add.tdescription)
    await message.answer("Enter description:")

@dp.message(Add.tdescription)
async def show_calendar(message: Message, state: Add, ):
    await state.update_data(tdescription = message.text)
    await state.set_state (Add.tdate)
    await message.answer("Enter date:", reply_markup=await SimpleCalendar(locale=await get_user_locale(message.from_user)).start_calendar())

@dp.callback_query(SimpleCalendarCallback.filter(), Add.tdate)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: Add):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}',
        )
        data = await state.get_data()
        name = data.get("tname")
        description = data.get("tdescription")
        date = date.strftime("%d/%m/%Y")
        cursor.execute("INSERT INTO tasks (name, description, date) VALUES (?, ?, ?)", (name, description, date))
        await callback_query.message.answer("Task added successfully!", reply_markup=kbs.main)
        conn.commit()

@dp.message(F.text == "Quit")
async def quit(message: Message):
    await message.reply("Goodbye!")


@dp.message(F.text == "Delete your tasks")
async def delete_task(message: Message):
    await message.reply("Choose an option:", reply_markup=kbs.delete)

@dp.message(F.text == "Delete all")
async def delete_all(message: Message):
    cursor.execute("DELETE FROM tasks")
    conn.commit()
    await message.reply("All tasks deleted successfully!", reply_markup=kbs.main)

@dp.message(F.text == "Delete one task")
async def delete_one_task(message: Message, state: delete):
    await message.reply("Enter the name of the task you want to delete:")
    await state.set_state(delete.dname)

@dp.message(delete.dname)
async def delete_task_by_name(message: Message, state: delete):
    await state.update_data(dname=message.text)
    name = message.text
    print(name)
    cursor.execute("DELETE FROM tasks WHERE TRIM(LOWER(name)) = TRIM(LOWER(?))", (name,))
    print(f"DELETE FROM tasks WHERE name='{name}'")
    conn.commit()
    await message.reply("Task deleted successfully!", reply_markup=kbs.main)


@dp.message(F.text == "Back")
async def back(message: Message):
    await message.reply("Choose an option:", reply_markup=kbs.main)

@dp.message(F.text == "View all")
async def view_all(message: Message):
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    if tasks:
        for task in tasks:
            await message.reply(f"Task: {task[1]}\nDescription: {task[2]}\nDate: {task[3]}")
    else:
        await message.reply("No tasks found.")
## setting polling
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
