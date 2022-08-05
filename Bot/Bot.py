import json
from os import getenv

import aiogram.utils.markdown as fmt
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from Parser.Parser import get_card_link

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token, parse_mode='html')
dp = Dispatcher(bot, storage=MemoryStorage())

start_buttons = ['GTX1650', 'GTX1660', 'RTX2060',
                 'RTX3050', 'RTX3060', 'RTX3070',
                 'RTX3070TI', 'RTX3080', 'RTX3090']


class Video(StatesGroup):
    wait_for_name = State()
    wait_for_choice = State()
    # Search = State()


@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_menu.add(*start_buttons)

    await message.answer("Привет, какую видеокарту будем парсить?", reply_markup=start_menu)
    await Video.wait_for_name.set()


@dp.message_handler(state=Video.wait_for_name)
async def inp(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['wait_for_name'] = message.text

    if message.text in start_buttons:
        choice_buttons = ['Список', 'CSV файл']
        keyboard_choice = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_choice.add(*choice_buttons)
        await message.answer(f'Как отправить данные по {message.text} ?', reply_markup=keyboard_choice)
        await Video.wait_for_choice.set()


@dp.message_handler(state=Video.wait_for_choice)
async def csv(message: types.Message, state: FSMContext):
    await message.answer("Секунду...загружаю....")
    async with state.proxy() as data:
        input_search = data['wait_for_name']
    if message.text == 'Список':
        get_card_link(search=input_search)

        with open('../venv/result_txt.json', encoding='utf-8') as file:
            dict = json.load(file)

        for key in dict:
            rw = (key, dict[key])
            await message.answer(
                fmt.text(
                    fmt.text(fmt.hbold(key)),
                    # fmt.text("Старая цена:", fmt.hstrikethrough(50), "рублей"),
                    fmt.text("Цена:", fmt.hbold(dict[key])),
                    sep="\n"
                ), parse_mode="HTML"
            )


    elif message.text == 'CSV файл':
        file = get_card_link(search=input_search)
        return await message.reply_document(open(file, 'rb'))

    await state.finish()


def main():
    executor.start_polling(dp, skip_updates=False)


if __name__ == "__main__":
    main()
