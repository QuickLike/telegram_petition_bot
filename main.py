import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from database import add_user, add_petition, get_data
import markups
from states import Petition

dp = Dispatcher()
load_dotenv()
token = os.getenv('BOT_TOKEN')
bot = Bot(token)

USER_ID = os.getenv('USER_ID')


@dp.message(Command('start'))
async def start(message: types.Message):
    add_user(message)
    await message.answer(
        text='Добро пожаловать!\n\nДля составления обращения нажмите на кнопку ниже👇',
        reply_markup=markups.create_petition_markup
    )


@dp.callback_query(F.data.in_(['petition', 'discard']))
async def petition_write(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer('Создаём обращение...')
    await state.set_state(Petition.text)
    await callback.message.answer('Пожалуйста, оставьте Ваше обращение👇')


@dp.message(Petition.text)
async def petition_check(message: types.Message, state: FSMContext):
    await message.answer(
        text=f"Пожалуйста, проверьте Ваше обращение: \n<i>{message.text}</i>",
        parse_mode='HTML'
    )
    add_petition(message)
    await state.update_data(text=message.text)
    await asyncio.sleep(2)
    await message.answer(
        text='Всё верно?',
        reply_markup=markups.check_petition_markup
    )


@dp.callback_query(F.data == 'accept')
async def petition_send(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.message.chat.id
    user_data, petitions_data = get_data(user_id)
    await callback.message.answer('Спасибо за обращение!\nСкоро я с Вами свяжусь!')
    first_name = user_data[2] or ''
    last_name = user_data[3] or ''
    username = user_data[1]
    message_text = (
        f"Обращение от пользователя {'@' + username if username else ''} {first_name} {last_name}"
    )
    await bot.send_message(USER_ID, message_text)
    await asyncio.sleep(2)
    try:
        await bot.forward_message(
            chat_id=USER_ID,
            from_chat_id=user_id,
            message_id=petitions_data[-1][-2]
        )
    except Exception as e:
        logging.exception(e)
    else:
        logging.info('Message forwarded from user %d', user_id)


@dp.message(F.text)
async def text_handle(message: types.Message):
    await message.answer(
        text='Для составления обращения нажмите на кнопку ниже👇',
        reply_markup=markups.create_petition_markup
    )


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='log.log',
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
