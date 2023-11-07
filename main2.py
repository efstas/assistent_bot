import aiogram
from aiogram import Bot, Dispatcher, executor, types
import config as cfg
import logging
import markups as nav
import asyncio
import time
import datetime


logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot)

date_object = datetime.date.today()


def is_admin(user_id):
    return str(user_id) == "241943423"  # Возвращает True, если пользователь имеет ID 241943423, иначе False

@dp.message_handler(commands=["bot_log"])
async def get_bot_log(message: types.Message):
    if is_admin(message.from_user.id):
        try:
            with open("bot.log", "r") as log_file:
                log_text = log_file.read()
            await bot.send_message(message.from_user.id, log_text)
        except FileNotFoundError:
            await bot.send_message(message.from_user.id, "Файл bot.log не найден.")
    else:
        await message.answer("Вы не являетесь администратором и не имеете доступа к этой команде.")


def read_stop_words():
    try:
        with open("stop_words.txt", "r") as file:
            words = [word.strip() for word in file.readlines()]
    except FileNotFoundError:
        words = []
    return words


def load_stop_words():
    with open("stop_words.txt", "r") as file:
        return [line.strip() for line in file]


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я бот. Если есть вопросы пиши создателю - @efstas.")


@dp.message_handler(commands=["user_id"])
async def send_message(message: types.Message):
    user_id = message.from_user.id
    await bot.send_message(user_id,f'User ID: {message.from_user.id}')

@dp.message_handler(commands=["stop_words"])
async def stopwords(message: types.Message):
    if is_admin(message.from_user.id):
        stop_words_list = "\n".join(load_stop_words())
        await bot.send_message(message.from_user.id, f'В данный момент я удаляю слова:\n\n{stop_words_list}')
    else:
        await message.answer("Вы не являетесь администратором и не имеете доступа к этой команде.")


@dp.message_handler(commands=["add_word"])
async def add_word(message: types.Message):
    if is_admin(message.from_user.id):
        text = message.get_args()
        if text:
            with open("stop_words.txt", "a") as file:
                file.write(text + "\n")
            await message.answer(f'Слово "{text}" успешно добавлено в список stop_words.')
        else:
            await message.answer("Вы не указали слово для добавления в список stop_words.")
    else:
        await message.answer("Вы не являетесь администратором и не имеете доступа к этой команде.")


def check_chat_member(chat_member):
    return chat_member['status'] != "left"


@dp.message_handler(content_types=['left_chat_member'])
async def delete_message_new_left(message: types.Message):
    await message.delete()


@dp.message_handler(content_types=["new_chat_members"])
async def user_joined(message: types.Message):
    await message.delete()
    for user in message.new_chat_members:
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time()+60)
        msg = await message.answer(f' Приветствую, {user.first_name} (@{user.username}) !\n'
                            "Чтобы отправлять сообщения, подпишись на канал @es_blog\n\n"
                            "У тебя есть одна минута, потом проверим :)\n\n"
                            "Присоединяйся: youtube.com/esblog  & instagram.com/es_blogde \n\n", reply_markup=nav.channelMenu)
        await asyncio.sleep(60)
        await msg.delete()

@dp.message_handler()
async def mess_handler(message: types.Message):
    stop_words = load_stop_words()
    if check_chat_member(await bot.get_chat_member(chat_id=cfg.CHANNEL_ID, user_id=message.from_user.id)):
        for word in stop_words:
            if word in message.text:
                await bot.send_message(chat_id=cfg.ADMIN_ID, text=f'❗ Дата нарушения - {date_object}\n\n'
                                                                  f'Ссылка на нарушителя: @{message.from_user.username}\n'
                                                                  f'ID нарушителя: ID{message.from_user.id}\n')
                await message.forward(chat_id=cfg.ADMIN_ID, disable_notification=True)
                await message.delete()
                message_stopwords = await message.answer(f'👮🏼♂️ Пришлось удалить сообщение, там были плохие слова...')
                await asyncio.sleep(120)
                await message_stopwords.delete()
            else:
                pass
    else:
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + 60)
        await message.delete()
        message_no_chat_member = await message.answer(f'@{message.from_user.username}, '
                                                      "чтобы отправлять сообщения, подпишись на канал @es_blog\n\n"
                                                      "У тебя есть одна минута, потом проверим :)\n\n"
                                                      "Присоединяйся: youtube.com/esblog  & instagram.com/es_blogde \n\n",
                                                      reply_markup=nav.channelMenu)

        try:
            await asyncio.sleep(60)
            await message_no_chat_member.delete()
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            pass


if __name__ == "__main__":
    print("bot go go go")
    executor.start_polling(dp, skip_updates=True)

