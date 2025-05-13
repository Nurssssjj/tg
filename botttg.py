import asyncio
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime

# === НАСТРОЙКИ ===
BOT_TOKEN = '7555630505:AAGWtcMBE5CBkRVz-fzc8En9X7BEFIr3qiQ'
ADMIN_ID = 6577960531
WHATSAPP_GROUP_CHAT_ID = '120363418881982137@g.us'

# === GREEN API НАСТРОЙКИ ===
GREEN_API_URL = 'https://7105.api.greenapi.com'
GREEN_API_ID_INSTANCE = '7105242193'
GREEN_API_TOKEN = '2efdd4fb9eaa4d82972f8c3fb20d13fe83636e14b4b3404daa'

# === ЦЕНЫ ===
PRICES = {
    5: 5000,
    10: 10000,
    50: 45000,
    100: 80000
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

perfumes = {
    'male': [
        {'name': 'Creed Aventus', 'description': 'Ananas, Bergamot, Musk'},
        {'name': 'Dior Sauvage', 'description': 'Bergamot, Pepper, Patchouli'},
        {'name': 'Tom Ford Oud Wood', 'description': 'Oud, Sandalwood, Amber'}
    ],
    'female': [
        {'name': 'Chanel Coco Mademoiselle', 'description': 'Orange, Jasmine, Vanilla'},
        {'name': 'Lancôme La Vie Est Belle', 'description': 'Iris, Vanilla, Praline'},
        {'name': 'Yves Saint Laurent Libre', 'description': 'Lavender, Vanilla, Amber'}
    ]
}

volumes = [5, 10, 50, 100]

class OrderForm(StatesGroup):
    product = State()
    volume = State()
    delivery = State()
    name = State()
    phone = State()
    city = State()
    address = State()
    lang = State()

user_langs = {}

texts = {
    "ru": {
        "welcome": "Привет! Выберите язык / Тілді таңдаңыз:",
        "choose_lang": "Выберите язык / Тілді таңдаңыз",
        "catalog": "Выберите категорию:",
        "male": "Мужской парфюм",
        "female": "Женский парфюм",
        "volume": "Выберите объём:",
        "delivery": "Выберите способ доставки:",
        "name": "Введите ваше имя:",
        "phone": "Введите номер телефона:",
        "city": "Введите город:",
        "address": "Введите адрес (улица, дом, кв):",
        "done": "Спасибо! Заказ принят.",
        "admin_panel": "Панель администратора",
        "whatsapp": "📱 Отправить в WhatsApp",
        "error_whatsapp": "Ошибка при отправке в WhatsApp."
    },
    "kz": {
        "welcome": "Сәлем! Тілді таңдаңыз / Выберите язык:",
        "choose_lang": "Тілді таңдаңыз / Выберите язык",
        "catalog": "Санатты таңдаңыз:",
        "male": "Ерлер парфюмі",
        "female": "Әйелдер парфюмі",
        "volume": "Көлемін таңдаңыз:",
        "delivery": "Жеткізу түрін таңдаңыз:",
        "name": "Атыңызды енгізіңіз:",
        "phone": "Телефон нөмірін енгізіңіз:",
        "city": "Қаланы енгізіңіз:",
        "address": "Мекенжайыңызды енгізіңіз (көшесі, үйі, пәтері):",
        "done": "Рақмет! Тапсырыс қабылданды.",
        "admin_panel": "Әкімші панелі",
        "whatsapp": "📱 WhatsApp-қа жіберу",
        "error_whatsapp": "WhatsApp-қа жіберу кезінде қате пайда болды."
    }
}

def t(lang, key):
    return texts.get(lang, texts['ru'])[key]

async def send_whatsapp_message(chat_id: str, message: str) -> bool:
    url = f"{GREEN_API_URL}/waInstance{GREEN_API_ID_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"
    payload = {
        "chatId": chat_id,
        "message": message
    }
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка при отправке в WhatsApp: {e}")
        return False

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="Қазақша", callback_data="lang_kz")]
    ])
    await message.answer(t("ru", "welcome"), reply_markup=keyboard)
    await state.set_state(OrderForm.lang)

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    user_langs[callback.from_user.id] = lang
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "male"), callback_data='male')],
        [InlineKeyboardButton(text=t(lang, "female"), callback_data='female')]
    ])
    await callback.message.answer(t(lang, "catalog"), reply_markup=keyboard)
    await callback.answer()

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("Доступ запрещён")
    lang = user_langs.get(message.from_user.id, 'ru')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "whatsapp"), url=f"https://chat.whatsapp.com/BRyFvffIg6O3Oie6BuFMbv")]
    ])
    await message.answer(t(lang, "admin_panel"), reply_markup=keyboard)

@dp.message(Command("catalog"))
async def catalog(message: Message):
    lang = user_langs.get(message.from_user.id, 'ru')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "male"), callback_data='male')],
        [InlineKeyboardButton(text=t(lang, "female"), callback_data='female')]
    ])
    await message.answer(t(lang, "catalog"), reply_markup=keyboard)

@dp.callback_query(F.data.in_(['male', 'female']))
async def show_perfumes(callback: CallbackQuery):
    lang = user_langs.get(callback.from_user.id, 'ru')
    category = callback.data
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=perfume['name'], callback_data=f"order_{perfume['name'].replace(' ', '_')}")]
        for perfume in perfumes[category]
    ])
    await callback.message.edit_text(t(lang, 'catalog'), reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data.startswith('order_'))
async def choose_volume(callback: CallbackQuery, state: FSMContext):
    product_name = callback.data.replace('order_', '').replace('_', ' ')
    await state.update_data(product=product_name)
    lang = user_langs.get(callback.from_user.id, 'ru')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{v} мл - {PRICES[v]} KZT", callback_data=f"volume_{v}")]
        for v in volumes
    ])
    await callback.message.answer(t(lang, "volume"), reply_markup=keyboard)
    await state.set_state(OrderForm.volume)
    await callback.answer()

@dp.callback_query(F.data.startswith("volume_"), StateFilter(OrderForm.volume))
async def choose_delivery(callback: CallbackQuery, state: FSMContext):
    volume = int(callback.data.replace('volume_', ''))
    await state.update_data(volume=volume, price=PRICES[volume])
    lang = user_langs.get(callback.from_user.id, 'ru')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Межгород (Казпочта)", callback_data='delivery_kazpost')],
        [InlineKeyboardButton(text="Город (Яндекс)", callback_data='delivery_yandex')]
    ])
    await callback.message.answer(t(lang, "delivery"), reply_markup=keyboard)
    await state.set_state(OrderForm.delivery)
    await callback.answer()

@dp.callback_query(StateFilter(OrderForm.delivery))
async def ask_name(callback: CallbackQuery, state: FSMContext):
    await state.update_data(delivery='Казпочта' if callback.data == 'delivery_kazpost' else 'Яндекс Доставка')
    lang = user_langs.get(callback.from_user.id, 'ru')
    await callback.message.answer(t(lang, "name"))
    await state.set_state(OrderForm.name)
    await callback.answer()

@dp.message(StateFilter(OrderForm.name))
async def ask_phone(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    lang = user_langs.get(message.from_user.id, 'ru')
    await message.answer(t(lang, "phone"))
    await state.set_state(OrderForm.phone)

@dp.message(StateFilter(OrderForm.phone))
async def ask_city(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    lang = user_langs.get(message.from_user.id, 'ru')
    await message.answer(t(lang, "city"))
    await state.set_state(OrderForm.city)

@dp.message(StateFilter(OrderForm.city))
async def ask_address(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    lang = user_langs.get(message.from_user.id, 'ru')
    await message.answer(t(lang, "address"))
    await state.set_state(OrderForm.address)

@dp.message(StateFilter(OrderForm.address))
async def finish_order(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    lang = user_langs.get(message.from_user.id, 'ru')
    order_text = (
        f"Новый заказ\n"
        f"Товар: {data['product']} ({data['volume']} мл)\n"
        f"Цена: {data['price']} KZT\n"
        f"Доставка: {data['delivery']}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Город: {data['city']}\n"
        f"Адрес: {data['address']}\n"
        f"WhatsApp: https://wa.me/{data['phone']}"
    )

    whatsapp_encoded_text = order_text.replace('\n', '%0A')
    await bot.send_message(chat_id=-1002280644534, text=order_text)

    whatsapp_success = await send_whatsapp_message(WHATSAPP_GROUP_CHAT_ID, order_text)
    if not whatsapp_success:
        await message.answer(t(lang, "error_whatsapp"))

    await message.answer(t(lang, "done"))
    await message.answer("Спасибо! Ваш заказ принят. Менеджер скоро свяжется с вами.")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
