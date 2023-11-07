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


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я бот. Если есть вопросы пиши создателю - @efstas.")

@dp.message_handler(commands=["user_id"])
async def send_message(message: types.Message):
    user_id = message.from_user.id
    await bot.send_message(user_id,f'User ID: {message.from_user.id}')

@dp.message_handler(commands=["stop_words"])
async def stopwords(message: types.Message):
    words_list = "\n".join(cfg.WORDS)
    await bot.send_message(message.from_user.id, f'В данный момент я удаляю слова:\n\n{words_list}')


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
    if check_chat_member(await bot.get_chat_member(chat_id=cfg.CHANNEL_ID, user_id=message.from_user.id)):
        for word in cfg.WORDS:
            if word in message.text:
                await bot.send_message(chat_id=241943423, text=f'❗ Дата нарушения - {date_object}\n\n'
                                                           f'Ссылка на нарушителя: @{message.from_user.username}\n'
                                                           f'ID нарушителя: ID{message.from_user.id}\n')
                await message.forward(chat_id=241943423, disable_notification=True)
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
        await asyncio.sleep(60)
        await message_no_chat_member.delete()


if __name__ == "__main__":
    print("bot go go go")
    executor.start_polling(dp, skip_updates=True)
