import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
import os
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '8047134791:AAGwYVEaa9uSDdkyuLfKImAdldpzn8580_4'
ADMIN_ID = 7688865252

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_reply = State()

# Красивая разметка приветствия
WELCOME_TEXT = (
    '<b>👋 ᴨᴩиʙᴇᴛ!</b>\n'
    '϶ᴛоᴛ боᴛ ᴄоздᴀн ᴄᴨᴇциᴀᴧьно дᴧя ᴛᴇх, у ᴋоᴦо <b>ᴄᴨᴀʍ-бᴧоᴋ</b> и нᴇᴛ ʙозʍожноᴄᴛи нᴀᴨиᴄᴀᴛь ᴨᴇᴩʙыʍ.\n'
    'ᴇᴄᴧи ᴛы хочᴇɯь ᴄʙязᴀᴛьᴄя ᴄо ʍной — ᴨᴩоᴄᴛо нᴀᴨиɯи ᴄюдᴀ, и я обязᴀᴛᴇᴧьно ᴛᴇбᴇ <b>оᴛʙᴇчу</b>!\n\n'
    '<i>✉️ жду ᴛʙоᴇᴦо ᴄообщᴇния!</i>'
)

# Клавиатура с кнопкой "Написать"
def get_write_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton('✍️ нᴀᴨиᴄᴀᴛь', callback_data='write_message'))
    return kb

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=get_write_keyboard())

# Обработка нажатия на кнопку "Написать"
@dp.callback_query_handler(Text(equals='write_message'))
async def prompt_for_message(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer('✏️ нᴀᴨиɯи ᴄʙоё ᴄообщᴇниᴇ, и я ᴨᴇᴩᴇдᴀʍ ᴇᴦо ʀᴇᴄᴏᴅᴇ!')
    await UserStates.waiting_for_message.set()

@dp.message_handler(state=UserStates.waiting_for_message, content_types=types.ContentTypes.TEXT)
async def handle_user_message(message: types.Message, state: FSMContext):
    # Отправляем админу
    user = message.from_user
    text = (
        f'<b>ноʙоᴇ ᴄообщᴇниᴇ!</b>\n'
        f'👤 <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{user.username if user.username else "Нет"}\n'
        f'🆔 <b>ɪᴅ:</b> <code>{user.id}</code>\n\n'
        f'<b>ᴄообщᴇниᴇ:</b>\n{message.text}'
    )
    reply_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('оᴛʙᴇᴛиᴛь', callback_data=f'reply_{user.id}')
    )
    await bot.send_message(ADMIN_ID, text, reply_markup=reply_markup)
    await message.answer('✅ ᴄообщᴇниᴇ оᴛᴨᴩᴀʙᴧᴇно ʀᴇᴄᴏᴅᴇ ожидᴀйᴛᴇ оᴛʙᴇᴛᴀ.')
    await state.finish()

# Обработка нажатия "Ответить" у админа
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('reply_'), user_id=ADMIN_ID)
async def admin_reply_prompt(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data.split('_')[1])
    await call.message.answer(f'✍️ нᴀᴨиɯиᴛᴇ оᴛʙᴇᴛ дᴧя ᴨоᴧьзоʙᴀᴛᴇᴧя <code>{user_id}</code>')
    await state.update_data(reply_to=user_id)
    await UserStates.waiting_for_reply.set()

@dp.message_handler(state=UserStates.waiting_for_reply, user_id=ADMIN_ID, content_types=types.ContentTypes.TEXT)
async def admin_send_reply(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('reply_to')
    if user_id:
        await bot.send_message(user_id, f'📩 <b>оᴛʙᴇᴛ оᴛ ʀᴇᴄᴏᴅᴇ:</b>\n\n{message.text}', reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('Ответить', callback_data='write_message')
        ))
        await message.answer('✅ оᴛʙᴇᴛ оᴛᴨᴩᴀʙᴧᴇн!')
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True) 