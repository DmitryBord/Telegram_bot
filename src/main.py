from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
import os

from openai import OpenAI
from gtts import gTTS
from io import BytesIO
from keyboard import markup_start, markup_talk, markup_find, btn_main_menu, markup_stop

from scrapping import parse
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class ClientState(StatesGroup):
    talk = State()
    talk_audio = State()
    talk_text = State()

    deal_type = State()
    number_rooms = State()
    max_price = State()


CLIENT = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.proxyapi.ru/openai/v1",
)

STORAGE = MemoryStorage()
BOT = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))  # Создаем экземпляр бота, подключаясь к API telegram
DP = Dispatcher(BOT, storage=STORAGE)  # Управление ботом будет через диспетчер


HELP_COMMAND = """<b>/start</b> - <em>starts the bot</em>
<b>/talk</b> - <em>Talk with AI 🤖</em>
<b>/find</b> - <em>Find apartments 🏘</em>
<b>/help</b> - <em>shows list of commands</em>
<b>/description</b> - <em>shows description of the bot</em>"""


async def chat_with_ai(text):
    response = CLIENT.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{"role": "user", "content": text}],
    )
    reply = response.choices[0].message.content
    return reply


async def check_file(file_name):
    if os.path.exists(file_name):
        return True
    else:
        return False


@DP.message_handler(commands=['start'])
async def handler_start(message: types.Message):
    await message.reply("Hi, Welcome to our bot!",
                        reply_markup=markup_start)
    await message.delete()


@DP.message_handler(Text(equals=["Help 🛟", "Help", "/help"]))
async def handler_help(message):
    await message.answer(HELP_COMMAND, parse_mode="HTML")
    await message.delete()


@DP.message_handler(Text(equals=["Description", "/description"]))
async def handler_description(message):
    await message.answer("This bot can just find an apartment in Moscow and just talk")
    await message.delete()


# --------------------------------------------------- Методы для поиска жилья
@DP.message_handler(Text(equals=["Find apartments 🏘", "/find"]))
async def handler_find(message: types.Message):
    await ClientState.deal_type.set()
    await message.answer("Please, enter what do you wanna rent or sale?",
                         reply_markup=markup_find.add(btn_main_menu) if len(markup_find.keyboard) == 1 else markup_find)


@DP.message_handler(Text(equals=["Rent", "Sale"]), state=ClientState.deal_type)
async def handler_deal_type(message: types.Message, state: FSMContext):
    if message.text == "Rent":
        async with state.proxy() as data:
            data["deal"] = message.text.lower()
    elif message.text == "Sale":
        async with state.proxy() as data:
            data["deal"] = message.text.lower()
    await ClientState.next()
    await message.answer("Please, enter number of rooms", reply_markup=markup_stop)


@DP.message_handler(lambda message: message.text != "Main menu", state=ClientState.number_rooms)
async def handler_rooms(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Please, enter number of rooms")
    else:
        async with state.proxy() as data:
            data["number_rooms"] = message.text
        await ClientState.next()
        await message.answer("Enter the maximum rental/sale price")


@DP.message_handler(lambda message: message.text != "Main menu", state=ClientState.max_price)
async def handler_max_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Please, enter maximum rental price")
    else:
        async with state.proxy() as data:
            data["max_price"] = int(message.text)

        async with state.proxy() as data:
            await message.answer("Please, wait...", reply_markup=ReplyKeyboardRemove())
            parse(data["deal"], data["number_rooms"], data["max_price"])

        if await check_file("apartments.xlsx"):
            await message.answer("Success!", reply_markup=markup_start)
            with open(f"apartments.xlsx", "rb") as f:
                await message.answer_document(document=f)
        else:
            await message.answer("Something went wrong. Tyr it again soon", reply_markup=markup_start)
        await state.finish()


# --------------------------------------------------- Методы для общения с AI
@DP.message_handler(Text(equals=["Talk with AI 🤖", "/talk"]))
async def handler_talk(message: types.Message):
    await ClientState.talk.set()
    await message.reply("How do you want the AI to respond to you with an audio or text message?",
                        reply_markup=markup_talk.add(btn_main_menu) if len(markup_talk.keyboard) == 1 else markup_talk)


@DP.message_handler(Text(equals="Audio"), state=[ClientState.talk, ClientState.talk_text])
async def handler_talk(message: types.Message):
    await ClientState.talk_audio.set()
    await message.answer("What about would you like to talk?")


@DP.message_handler(Text(equals="Text"), state=[ClientState.talk, ClientState.talk_audio])
async def handler_talk(message: types.Message):
    await ClientState.talk_text.set()
    await message.answer("What about would you like to talk?")


@DP.message_handler(Text(equals="Main menu"), state="*")
async def handler_stop(message: types.Message, state: FSMContext):
    await message.answer("You ended the conversation.", reply_markup=markup_start)
    await message.delete()
    await state.finish()


@DP.message_handler(content_types="text", state=ClientState.talk_text)
async def handler_echo(message: types.Message):
    response = await chat_with_ai(message.text)
    await message.answer(response)


@DP.message_handler(content_types="text", state=ClientState.talk_audio)
async def handler_echo(message: types.Message):
    response = await chat_with_ai(message.text)
    tts = gTTS(response, lang='ru')
    voice = BytesIO()
    tts.write_to_fp(voice)
    voice.seek(0)
    await message.answer_voice(voice)


@DP.message_handler(content_types="text", state=[ClientState.talk, None])
async def handler_echo(message: types.Message):
    await message.reply("To start interacting with the bot, enter '/start'")


async def on_startup(_):
    print("I started the bot!")


if __name__ == '__main__':
    executor.start_polling(DP, skip_updates=True,
                           on_startup=on_startup)
