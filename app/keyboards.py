from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, WebAppInfo

from config import CHANNELS

start_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text= "Русский", callback_data="Russian"),InlineKeyboardButton(text="English", callback_data="English")]
])





main_russia = ReplyKeyboardMarkup(keyboard=
[
    [
        KeyboardButton(text="🕹️ Играть")
    ],
    [
        KeyboardButton(text="💸Пресейл"),
        KeyboardButton(text="🤝 Реферальная ссылка")
    ],
    [
        KeyboardButton(text="📲 Подключить кошелек"),
        KeyboardButton(text="💰 Награды")
    ],
    [
        KeyboardButton(text="⚙️ Профиль"),
        KeyboardButton(text="🌐 Язык")
    ],
],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите пункт меню.'
)

main_english = ReplyKeyboardMarkup(keyboard=
[
    [
        KeyboardButton(text="🕹️ Play")
    ],
    [
        KeyboardButton(text="💸Presale"),
        KeyboardButton(text="🤝 Referral Link")
    ],
    [
        KeyboardButton(text="📲 Connect Wallet"),
        KeyboardButton(text="💰 Rewards")
    ],
    [
        KeyboardButton(text="⚙️ Profile"),
        KeyboardButton(text="🌐 Language")
    ],
],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Select a menu item.'
)


main_presell_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="50 TON ", callback_data="50 TON",url='ton://transfer/UQD9NwqXuJ1MktBwr5tkmVXYM-4dFeNcE3x8R0_KjgxhyP-Y?amount=50000000000&text=Donation'),
     InlineKeyboardButton(text="100 TON ", callback_data="100 TON",url='ton://transfer/UQD9NwqXuJ1MktBwr5tkmVXYM-4dFeNcE3x8R0_KjgxhyP-Y?amount=100000000000 &text=Donation'),
     InlineKeyboardButton(text="200 TON ", callback_data="200 TON",url='ton://transfer/UQD9NwqXuJ1MktBwr5tkmVXYM-4dFeNcE3x8R0_KjgxhyP-Y?amount=200000000000&text=Donation')],
    [InlineKeyboardButton(text="Любое кол-во ",url='ton://transfer/UQD9NwqXuJ1MktBwr5tkmVXYM-4dFeNcE3x8R0_KjgxhyP-Y')],
    [InlineKeyboardButton(text="🔚 Вернуться в меню",callback_data="back_menu")]
], resize_keyboard=True, one_time_keyboard=True
)

# main_russia_connect = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text= "Подключить Wallet",url='https://example.com' )]])

main_presell_en = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="50 TON", callback_data="50 TON_en", url='ton://transfer/UQD9NwqXuJ1MktBwr5tkmVXYM-4dFeNcE3x8R0_KjgxhyP-Y?amount=50000000000&text=Donation'),
     InlineKeyboardButton(text="100 TON", callback_data="100 TON_en", url='ton://transfer/UQD9NwqXuJ1MktBwr5tkmVXYM-4dFeNcE3x8R0_KjgxhyP-Y?amount=100000000000 &text=Donation'),
     InlineKeyboardButton(text="200 TON", callback_data="200 TON_en", url='ton://transfer/UQD9NwqXuJ1MktBwr5tkmVXYM-4dFeNcE3x8R0_KjgxhyP-Y?amount=200000000000&text=Donation')],
    [InlineKeyboardButton(text="Any amount", url='ton://transfer/UQD9NwqXuJ1MktBwr5tkmVXYM-4dFeNcE3x8R0_KjgxhyP-Y')],
    [InlineKeyboardButton(text="🔚 Back to menu", callback_data="back_menu_en")]
], resize_keyboard=True, one_time_keyboard=True)

# main_en_connect = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text="Connect Wallet", url='https://example.com')]
# ])


admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Аналитика", callback_data="admin_analytics")],
    ], resize_keyboard=True, one_time_keyboard=True)




def generate_subscribe_keyboard():
    keyboard = InlineKeyboardBuilder()
    # Добавляем кнопки для каждого канала из списка
    for name, chat_id, url in CHANNELS:
        keyboard.add(InlineKeyboardButton(text=name, url=url))
    # Добавляем кнопку для проверки подписки
    keyboard.row()  # Можно использовать для размещения следующей кнопки в новой строке
    keyboard.add(InlineKeyboardButton(text="✅ Проверить подписку", callback_data="checksub"), InlineKeyboardButton(text="🔚Назад в меню",callback_data="back_menu"))
    return keyboard.adjust(1).as_markup()

subscribe_channels = generate_subscribe_keyboard()


def generate_subscribe_keyboard_en():
    keyboard = InlineKeyboardBuilder()
    # Добавляем кнопки для каждого канала из списка
    for name, chat_id, url in CHANNELS:
        keyboard.add(InlineKeyboardButton(text=name, url=url))
    # Добавляем кнопку для проверки подписки
    keyboard.row()  # Можно использовать для размещения следующей кнопки в новой строке
    keyboard.add(InlineKeyboardButton(text="✅ Check subject", callback_data="checksub_en"), InlineKeyboardButton(text="🔚Back to menu",callback_data="back_menu_en"))
    return keyboard.adjust(1).as_markup()

subscribe_channels_en = generate_subscribe_keyboard_en()
