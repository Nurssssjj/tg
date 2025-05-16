import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import requests

BOT_TOKEN = '7555630505:AAGWtcMBE5CBkRVz-fzc8En9X7BEFIr3qiQ'
ADMIN_ID = 6577960531
WHATSAPP_GROUP_CHAT_ID = '120363418881982137@g.us'
GREEN_API_URL = 'https://7105.api.greenapi.com'
GREEN_API_ID_INSTANCE = '7105242193'
GREEN_API_TOKEN = '2efdd4fb9eaa4d82972f8c3fb20d13fe83636e14b4b3404daa'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

perfumes = {
    'male': [
        'Creed Aventus', 'Dior Sauvage', 'Tom Ford Oud Wood',
        'Bleu de Chanel', 'Versace Eros', 'Acqua di Gio'
    ],
    'female': [
        'Chanel Coco Mademoiselle', 'La Vie Est Belle', 'YSL Libre',
        "Dior J'adore", 'Gucci Bloom', 'Good Girl'
    ]
}

PRICES = {
    'Creed Aventus': {5: 6000, 10: 11000, 50: 49000, 100: 89000},
    'Dior Sauvage': {5: 5000, 10: 9500, 50: 44000, 100: 85000},
    'Tom Ford Oud Wood': {5: 7000, 10: 12000, 50: 52000, 100: 92000},
    'Bleu de Chanel': {5: 5500, 10: 10000, 50: 46000, 100: 87000},
    'Versace Eros': {5: 4800, 10: 9000, 50: 43000, 100: 84000},
    'Acqua di Gio': {5: 5300, 10: 9800, 50: 45000, 100: 86000},
    'Chanel Coco Mademoiselle': {5: 6000, 10: 11000, 50: 49000, 100: 89000},
    'La Vie Est Belle': {5: 5000, 10: 9500, 50: 44000, 100: 85000},
    'YSL Libre': {5: 7000, 10: 12000, 50: 52000, 100: 92000},
    "Dior J'adore": {5: 5800, 10: 10500, 50: 47000, 100: 88000},
    'Gucci Bloom': {5: 5100, 10: 9700, 50: 45000, 100: 86000},
    'Good Girl': {5: 5300, 10: 9900, 50: 46000, 100: 87000}
}

texts = {
    "kz": {
        "main_menu": "Басты мәзірге оралдыңыз. Таңдаңыз:",
        "select_gender": "Парфюм категориясын таңдаңыз:",
        "select_perfume": "Ароматты таңдаңыз:",
        "select_volume": "Көлемін таңдаңыз:",
        "select_delivery": "Жеткізу әдісін таңдаңыз:",
        "invalid_perfume": "Кешіріңіз, ондай аромат жоқ. Басқасын таңдаңыз:",
        "invalid_volume": "Кешіріңіз, мұндай көлем жоқ. Басқасын таңдаңыз:",
        "back": "🔙 Назад",
        "home": "📦 Менюға оралу"
    },
    "ru": {
        "main_menu": "Вы вернулись в главное меню. Выберите:",
        "select_gender": "Выберите категорию парфюма:",
        "select_perfume": "Выберите аромат:",
        "select_volume": "Выберите объём:",
        "select_delivery": "Выберите способ доставки:",
        "invalid_perfume": "Извините, такого аромата нет. Пожалуйста, выберите другой:",
        "invalid_volume": "Извините, объём недействителен. Пожалуйста, выберите другой:",
        "back": "🔙 Назад",
        "home": "📦 Вернуться в меню"
    }
}

class OrderForm(StatesGroup):
    gender = State()
    product = State()
    volume = State()
    delivery = State()
    name = State()
    phone = State()
    city = State()
    address = State()

def get_main_menu(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👨 Мужской парфюм"), KeyboardButton(text="👩 Женский парфюм")],
            [KeyboardButton(text=texts[lang]["home"])]
        ], resize_keyboard=True
    )

def get_perfume_menu(gender, lang):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=name)] for name in perfumes[gender]] + [[KeyboardButton(text=texts[lang]["back"]), KeyboardButton(text=texts[lang]["home"])]],
        resize_keyboard=True
    )

def get_volume_menu(product, lang):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"{v} мл - {PRICES[product][v]} ₸")] for v in PRICES[product]] + [[KeyboardButton(text=texts[lang]["back"]), KeyboardButton(text=texts[lang]["home"])]],
        resize_keyboard=True
    )

def get_delivery_menu(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Казпочта")],
            [KeyboardButton(text="🚕 Яндекс Доставка")],
            [KeyboardButton(text=texts[lang]["back"]), KeyboardButton(text=texts[lang]["home"])]
        ], resize_keyboard=True
    )

async def send_whatsapp_message(chat_id: str, message: str) -> bool:
    url = f"{GREEN_API_URL}/waInstance{GREEN_API_ID_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"
    payload = {"chatId": chat_id, "message": message}
    try:
        r = requests.post(url, json=payload)
        return r.status_code == 200
    except Exception as e:
        print("Ошибка WhatsApp:", e)
        return False

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    lang_menu = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇰🇿 Қазақша"), KeyboardButton(text="🇷🇺 Русский")]], resize_keyboard=True
    )
    await message.answer("Тілді таңдаңыз / Выберите язык:", reply_markup=lang_menu)

@dp.message(F.text.in_(["🇰🇿 Қазақша", "🇷🇺 Русский"]))
async def set_language(message: Message, state: FSMContext):
    lang = "kz" if "Қазақша" in message.text else "ru"
    await state.update_data(lang=lang)
    await message.answer(texts[lang]["main_menu"], reply_markup=get_main_menu(lang))
    await state.set_state(OrderForm.gender)

@dp.message(F.text.in_([texts["kz"]["home"], texts["ru"]["home"]]))
async def back_to_main_menu(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "kz")
    await message.answer(texts[lang]["main_menu"], reply_markup=get_main_menu(lang))
    await state.set_state(OrderForm.gender)

@dp.message(StateFilter(OrderForm.gender))
async def select_gender(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "kz")
    if "Мужской" in message.text:
        await state.update_data(gender='male')
    elif "Женский" in message.text:
        await state.update_data(gender='female')
    else:
        return await message.answer(texts[lang]["select_gender"], reply_markup=get_main_menu(lang))
    
    data = await state.get_data()  # Обновляем данные после записи
    await message.answer(texts[lang]["select_perfume"], reply_markup=get_perfume_menu(data['gender'], lang))
    await state.set_state(OrderForm.product)

@dp.message(StateFilter(OrderForm.product))
async def select_product(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "kz")
    gender = data.get("gender")
    
    if message.text == texts[lang]["back"]:
        return await start(message, state)
    
    # Проверяем, есть ли выбранный аромат в списке категории
    if gender is None or message.text not in perfumes.get(gender, []):
        return await message.answer(texts[lang]["invalid_perfume"], reply_markup=get_perfume_menu(gender if gender else 'male', lang))
    
    await state.update_data(product=message.text)
    await message.answer(texts[lang]["select_volume"], reply_markup=get_volume_menu(message.text, lang))
    await state.set_state(OrderForm.volume)

@dp.message(StateFilter(OrderForm.volume))
async def select_volume(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "kz")

    if message.text == texts[lang]["back"]:
        await message.answer(texts[lang]["select_perfume"], reply_markup=get_perfume_menu(data['gender'], lang))
        return await state.set_state(OrderForm.product)

    try:
        # Ожидаем формат: "5 мл - 6000 ₸", поэтому берем первый элемент и пытаемся преобразовать в int
        volume = int(message.text.split()[0])
    except (ValueError, IndexError):
        return await message.answer(texts[lang]["invalid_volume"], reply_markup=get_volume_menu(data['product'], lang))

    if volume not in PRICES.get(data['product'], {}):
        return await message.answer(texts[lang]["invalid_volume"], reply_markup=get_volume_menu(data['product'], lang))

    await state.update_data(volume=volume)
    await state.update_data(price=PRICES[data['product']][volume])

    await message.answer(texts[lang]["select_delivery"], reply_markup=get_delivery_menu(lang))
    await state.set_state(OrderForm.delivery)

@dp.message(StateFilter(OrderForm.delivery))
async def delivery_select(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "kz")
    
    if message.text == texts[lang]["back"]:
        # Вернуться к выбору объёма
        await message.answer(texts[lang]["select_volume"], reply_markup=get_volume_menu(data['product'], lang))
        return await state.set_state(OrderForm.volume)
    
    # Обновляем выбор доставки
    await state.update_data(delivery=message.text)
    
    # Запрашиваем имя
    if lang == "kz":
        await message.answer("Атыңызды енгізіңіз:")
    else:
        await message.answer("Введите ваше имя:")
    
    await state.set_state(OrderForm.name)

@dp.message(StateFilter(OrderForm.name))
async def get_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "kz")

    await state.update_data(name=message.text)

    if lang == "kz":
        await message.answer("Телефон нөміріңізді енгізіңіз:")
    else:
        await message.answer("Введите номер телефона:")

    await state.set_state(OrderForm.phone)

@dp.message(StateFilter(OrderForm.phone))
async def get_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "kz")

    await state.update_data(phone=message.text)

    if lang == "kz":
        await message.answer("Қалаңызды енгізіңіз:")
    else:
        await message.answer("Введите ваш город:")

    await state.set_state(OrderForm.city)

@dp.message(StateFilter(OrderForm.city))
async def get_city(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "kz")

    await state.update_data(city=message.text)

    if lang == "kz":
        await message.answer("Мекенжайыңызды енгізіңіз (көшесі, үйі, пәтері):")
    else:
        await message.answer("Введите адрес (улица, дом, кв):")

    await state.set_state(OrderForm.address)

@dp.message(StateFilter(OrderForm.address))
async def confirm_order(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    lang = data.get("lang", "kz")

    text = (
        f"🧾 *Тапсырыс*\n" if lang == "kz" else f"🧾 *Заказ*\n"
    ) + (
        f"👃 Аромат: {data['product']} ({data['volume']} мл)\n"
        f"💰 Бағасы: {data['price']} ₸\n"
        f"🚚 Жеткізу: {data['delivery']}\n"
        f"👤 Аты: {data['name']}\n"
        f"📞 Тел: {data['phone']}\n"
        f"🏙 Қала: {data['city']}\n"
        f"🏠 Мекенжай: {data['address']}"
    )

    # Отправляем заказ в канал Telegram
    await bot.send_message(chat_id=-1002280644534, text=text, parse_mode="Markdown")

    # Отправляем админу
    await bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="Markdown")

    # Отправляем через WhatsApp API
    await send_whatsapp_message(WHATSAPP_GROUP_CHAT_ID, text)

    # Сообщаем пользователю
    await message.answer(
        "Рақмет! Тапсырысыңыз қабылданды. Менеджер хабарласады." if lang == "kz" else "Спасибо! Ваш заказ принят. Менеджер свяжется с вами.",
        reply_markup=get_main_menu(lang)
    )

    # Очищаем состояние
    await state.clear()

# Далее идут остальные хендлеры (select_gender, select_product и т.д.) — они уже были добавлены в Canvas.

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
