import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from database import add_user, add_petition, get_data, send_petition, get_petition
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
    await callback.answer('Обращение отправлено')
    await state.clear()
    user_id = callback.message.chat.id
    user_data, petitions_data = get_data(user_id)
    first_name = user_data[2] or ''
    last_name = user_data[3] or ''
    username = user_data[1]
    message_id = petitions_data[-1][-3]
    message_text = (
        f"Обращение от пользователя {'@' + username if username else ''} {first_name} {last_name}"
    )
    if not send_petition(user_id, message_id):
        await callback.message.answer('Спасибо за обращение!\nСкоро я с Вами свяжусь!')
        await callback.message.delete()

        accept_petition_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Принять',
                        callback_data=f'take_to_job-{user_id}-{message_id}',
                    )
                ]
            ]
        )

        await bot.send_message(
            chat_id=USER_ID,
            text=message_text,
            reply_markup=accept_petition_markup
        )
        await asyncio.sleep(2)
        try:
            await bot.forward_message(
                chat_id=USER_ID,
                from_chat_id=user_id,
                message_id=message_id
            )
        except Exception as e:
            logging.exception(e)
        else:
            logging.info('Message forwarded from user %d', user_id)
    else:
        await bot.send_message(user_id, 'Ваше обращение уже отправлено!')


@dp.callback_query(F.data.startswith('take_to_job'))
async def take_to_job(callback: types.CallbackQuery):
    await callback.answer('Обращение принято в работу')
    _, user_id, message_id = callback.data.split('-')
    petition_text = get_petition(user_id, message_id)
    await bot.send_message(
        chat_id=user_id,
        text=f'Ваше обращение принято в работу, его рассматривает администратор.\n\n<i>"{petition_text}"</i>',
        parse_mode='HTML'
    )
    await callback.message.edit_text('👇Обращение принято👇')


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
