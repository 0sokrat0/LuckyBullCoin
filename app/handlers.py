import aiogram
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram import Router, F, Bot
from aiogram.enums import ChatAction, ParseMode, ChatMemberStatus
import app.keyboards as kb
import random
import config as cfg
from database.database import Database
from config import CHANNELS



router = Router()
db = Database(cfg.db_config)


# Список стикеров
stickers = [
    "CAACAgIAAxkBAAEMFmVmPmsTsFIcuupxwLAYrqmGfk91vQACAQEAAladvQoivp8OuMLmNDUE",
    "CAACAgIAAxkBAAEMFmlmPms0kjm3Qj84IL3sMDWA4sufkgAC2A8AAkjyYEsV-8TaeHRrmDUE",
    "CAACAgIAAxkBAAEMFmtmPmtEAkkKmSBa44SzyKw4t3psxwACSwADUomRI8htaM0_6NrrNQQ",
    "CAACAgIAAxkBAAEMFpxmPpYUnxs4qdj40Vi5UbqMOUtnuQAC8iwAAnDW4UuITBkIiCOD3zUE",
    "CAACAgIAAxkBAAEMFwdmPzDucMmPsrsAASXqR7j4ULRqjmkAAkIQAAIzxSlJkA7UEacqSoI1BA"
]


@router.message(CommandStart())
async def send_welcome(message: Message):
    user_id = message.from_user.id
    tg_name = message.from_user.username
    referer_id = None
    args = message.text.split()

    if len(args) > 1:
        referer_id = args[1]

    if not db.user_exists(user_id):
        db.add_user(user_id, referer_id, tg_name)

    # Проверяем, превышено ли количество рефералов
    if referer_id and referer_id != str(user_id):
        num_referrals = db.get_referral_count(referer_id)
        if num_referrals < 5:
            db.add_bonus(referer_id, 100)  # Начисляем 100 бонусов за прямого реферала
            db.add_bonus(user_id, 50)  # Начисляем 50 бонусов новому пользователю
            db.increment_referral_count(referer_id)  # Увеличиваем счетчик рефералов

            try:
                await message.bot.send_message(referer_id,
                                               '<b>По вашей ссылке зарегистрировался новый пользователь!\nnew user has registered using your link</b>',
                                               parse_mode=ParseMode.HTML)
            except Exception as e:
                print(f"Ошибка при отправке сообщения рефереру: {e}")
        else:
            # Рассчитываем уменьшенный бонус за косвенные рефералы
            indirect_bonus = 100 * (0.5 ** (num_referrals - 5))
            if indirect_bonus >= 1:  # Проверяем, что бонус не слишком мал
                db.add_bonus(referer_id, indirect_bonus)

    random_sticker = random.choice(stickers)
    await message.answer_sticker(random_sticker)

    await message.answer(
        f"Приветствую, {message.from_user.first_name}!\n\n<b>🌐 Choose your language / выбери язык</b>",
        reply_markup=kb.start_main, parse_mode="HTML"
    )


@router.callback_query(F.data == "Russian")
async def russian(callback_query:CallbackQuery):
    await callback_query.answer('Russian')
    await callback_query.message.answer("*Lucky Bull* — это мемкоин, который символизирует наступление бычьего рынка. Если ты искатель приключений в мире крипты, присоединяйся к нам — покупай и играй!", reply_markup=kb.main_russia, parse_mode=ParseMode.MARKDOWN)


@router.callback_query(F.data == "English")
async def english(callback_query:CallbackQuery):
    await callback_query.answer('English')
    await callback_query.message.answer("*Lucky Bull* is a meme coin that symbolizes the onset of a bull market. If you are an adventurer in the world of crypto, join us — buy and play!", reply_markup=kb.main_english, parse_mode=ParseMode.MARKDOWN)

@router.callback_query(F.data == "back_menu")
async def back_menu(callback_query:CallbackQuery):
    await callback_query.answer("В меню")
    await callback_query.message.answer(f"Выберите пункт",reply_markup=kb.main_russia)

@router.callback_query(F.data == "back_menu_en")
async def back_menu(callback_query:CallbackQuery):
    await callback_query.answer("To menu")
    await callback_query.message.answer(f"Select a menu item",reply_markup=kb.main_english)

stickers_coders = [
    "CAACAgIAAxkBAAEMIUpmRmkET4E4CERSuSPgueS--SGh5wACclMAApc-AAFJ9R9UJhdpZ_U1BA",
    "CAACAgIAAxkBAAEMIUxmRmkIMAWpRsGfdYTXZttdor3z4gACiQoAAnFuiUvTl1zojCsDsDUE",
    "CAACAgIAAxkBAAEMIU5mRmkNjnpOTC6u-wfHwKT54ts_yQACIAkAAhhC7gjhiiCooToK2TUE",
    "CAACAgIAAxkBAAEMIVJmRmkS2oVGskP0hV4YWmcCMTTbugACLDYAAl_dqUgSAAFauJm7kMg1BA",
    "CAACAgIAAxkBAAEMIVRmRmkVp-wFXNCQ81n7v-cuRBw1cgAC-S4AAjeICUpKu11XLwOnnTUE"
]

@router.message(F.text == "💰 Награды")
async def show_rewards(message: Message):
    user_id = message.from_user.id
    num_referrals = db.count_referals(user_id)
    bonus_points = db.get_bonus_points(user_id)

    # Подготовка списка каналов с их статусами подписки
    subscription_status = []
    for channel_name, channel_id, _ in CHANNELS:  # Изменили порядок для доступа к имени и ID
        try:
            member = await message.bot.get_chat_member(channel_id, user_id)
            if member.status in ["member", "administrator", "creator"]:
                subscription_status.append(f"✅ - {channel_name} (+50 po)")
            else:
                subscription_status.append(f"❌ - {channel_name} (+50 po)")
        except Exception as e:
            print(f"Error checking channel {channel_name} subscription: {str(e)}")
            subscription_status.append(f"❌ - {channel_name} (+50 po)")  # Assume not subscribed on error

    subscriptions_list = "\n".join(subscription_status)

    await message.answer(
        f"🤝 Приглашенные друзья (<b>{num_referrals}/5</b>) (за каждого +100 поинтов)\n{subscriptions_list}\nУ вас <b>{bonus_points}</b> бонусных очков!",
        parse_mode=ParseMode.HTML,
        reply_markup=kb.generate_subscribe_keyboard()
    )

@router.message(F.text == "🕹️ Играть")
async def play_ru(message:Message):
    random_sticker = random.choice(stickers_coders)
    await message.answer_sticker(random_sticker)
    await message.answer("Мы рады, что ты уже готов ворваться в игру, но чтобы сделать ее качественнее нам надо еще немного времени",reply_markup=kb.main_russia)

@router.message(F.text == "🕹️ Play")
async def play_ru(message:Message):
    random_sticker = random.choice(stickers_coders)
    await message.answer_sticker(random_sticker)
    await message.answer("We are glad that you are ready to break into the game, but we need a little more time to make it better",reply_markup=kb.main_english)


@router.message(F.text == "💸Пресейл")
async def presell_ru(message:Message):
    pay_adress = f"UQD9NwqXuJ1MktBwr5tkmVXYM-4dFeNcE3x8R0_KjgxhyP-Y"
    await message.answer(f"Что бы участвовать в пресейле нужно отправить ton на адрес -\n"f"`{pay_adress}`", reply_markup=kb.main_presell_ru, parse_mode="Markdown")

@router.message(F.text == "📲 Подключить кошелек")
async def connect(message:Message):
    await message.answer("Подключить кошелек можно будет чуть позже",reply_markup=kb.main_russia)
    # await message.answer(f"подключи свой кошелек, чтобы получить бонусы и полностью насладиться игрой", reply_markup=kb.main_russia_connect, parse_mode=ParseMode.HTML)

@router.message(F.text =="⚙️ Профиль")
async def profile(message:Message):
    user_id = message.from_user.id
    num_referals = db.count_referals(message.from_user.id)
    bonus = db.get_bonus_points(user_id)
    # Ответ пользователю с информацией о профиле и количестве рефералов
    await message.answer(f"<u>Ваш профиль</u>\n\nID:<b> {message.from_user.id}</b>\nИмя:<b> {message.from_user.username}</b>\nКол-во рефералов:<b> {num_referals}</b>\nКол-во бонусов <b> {bonus}</b>", parse_mode=ParseMode.HTML,reply_markup=kb.main_russia)

@router.message(F.text =="🤝 Реферальная ссылка")
async def referal (message:Message):
    referral_link = f"https://t.me/{cfg.bot_name}?start={message.from_user.id}"
    response_text = (
        "Приглашайте друзей и занимайтесь совместным развитием! За первых 5 приглашённых — 500 бонусов сразу, и по 100 бонусов за каждого следующего.\n\n"
        "Ваша реферальная ссылка:\n"
        f"`{referral_link}`"  # Используем одинарные обратные кавычки для форматирования ссылки как код
    )

    await message.answer(response_text, parse_mode="Markdown", reply_markup=kb.main_russia)


async def check_user_subscriptions_and_add_bonuses(bot: Bot, user_id: int, db):
    successful_subscriptions = []
    for index, channel in enumerate(CHANNELS):
        channel_name, channel_id, channel_url = channel[0], channel[1], channel[2]
        bonus_amount = cfg.BONUSES[index]  # Получаем бонус, соответствующий каналу
        try:
            member = await bot.get_chat_member(channel_id, user_id)
            if member.status in ["member", "administrator", "creator"]:
                if not db.has_received_bonus_for_channel(user_id, channel_id):
                    db.add_bonus(user_id, bonus_amount)
                    db.mark_bonus_received_for_channel(user_id, channel_id)
                    successful_subscriptions.append(channel_name)
        except Exception as e:
            print(f"Error checking subscription for {channel_name} ({channel_id}): {str(e)}")
    return successful_subscriptions

async def check_all_subscriptions(bot: Bot, user_id: int):
    """ Проверяет, подписан ли пользователь на все каналы. Возвращает True, если подписан на все. """
    try:
        for _, channel_id, _ in CHANNELS:
            member = await bot.get_chat_member(channel_id, user_id)
            # Проверяем статусы, которые указывают на подписку пользователя
            if member.status not in ["member", "administrator", "creator"]:
                return False
        return True
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False


@router.message(F.text == "🌐 Язык")
async def language(message: Message):
    await message.answer("🌐 <b>Choose your language / выбери язык</b>",parse_mode=ParseMode.HTML,reply_markup=kb.start_main)

@router.message(F.text == "🌐 Language")
async def language(message: Message):
    await message.answer("🌐 <b>Choose your language / выбери язык</b>",parse_mode=ParseMode.HTML,reply_markup=kb.start_main)
async def check_user_subscriptions_and_add_bonuses(bot: Bot, user_id: int, db):
    successful_subscriptions = []
    for index, channel in enumerate(CHANNELS):
        channel_name, channel_id, channel_url = channel[0], channel[1], channel[2]
        bonus_amount = cfg.BONUSES[index]  # Получаем бонус, соответствующий каналу
        try:
            member = await bot.get_chat_member(channel_id, user_id)
            if member.status in ["member", "administrator", "creator"]:
                if not db.has_received_bonus_for_channel(user_id, channel_id):
                    db.add_bonus(user_id, bonus_amount)
                    db.mark_bonus_received_for_channel(user_id, channel_id)
                    successful_subscriptions.append(channel_name)
        except Exception as e:
            print(f"Error checking subscription for {channel_name} ({channel_id}): {str(e)}")
    return successful_subscriptions

async def check_all_subscriptions(bot: Bot, user_id: int):
    """ Проверяет, подписан ли пользователь на все каналы. Возвращает True, если подписан на все. """
    try:
        for _, channel_id, _ in CHANNELS:
            member = await bot.get_chat_member(channel_id, user_id)
            # Проверяем статусы, которые указывают на подписку пользователя
            if member.status not in ["member", "administrator", "creator"]:
                return False
        return True
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False

@router.callback_query(F.data == "checksub")
async def check_subscription(callback_query: CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id  # Используем правильный атрибут для получения ID пользователя

    # Проверяем, подписан ли пользователь на все каналы
    all_subscribed = await check_all_subscriptions(bot, user_id)

    if all_subscribed:
        # Отправка стикера через объект bot, а не через callback_query
        await bot.send_sticker(callback_query.from_user.id, "CAACAgIAAxkBAAEMIVxmRmu4e7_UAikXkBkCgRACCcNnngACrjAAAnx_uEp6KcLM_EAS-TUE")
        await callback_query.message.answer(
            "Вы уже подписаны на все доступные каналы и чаты!",
            reply_markup=kb.main_russia
        )
    else:
        successful_subscriptions = await check_user_subscriptions_and_add_bonuses(bot, user_id, db)
        if successful_subscriptions:
            subscriptions_list = ", ".join(successful_subscriptions)
            await callback_query.message.answer(
                f"Вы успешно подписаны на: {subscriptions_list}. Бонусы начислены.",
                reply_markup=kb.main_russia
            )
        else:
            await callback_query.message.answer(
                "Пожалуйста, подпишитесь на все каналы и чаты для получения бонусов.",
                reply_markup=kb.main_russia
            )

    await callback_query.answer()

@router.callback_query(F.data == "checksub_en")
async def check_subscription(callback_query: CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id

    # Проверяем, подписан ли пользователь на все каналы
    all_subscribed = await check_all_subscriptions(bot, user_id)

    if all_subscribed:
        # Отправка стикера через объект bot, а не через callback_query
        await bot.send_sticker(callback_query.from_user.id, "CAACAgIAAxkBAAEMIVxmRmu4e7_UAikXkBkCgRACCcNnngACrjAAAnx_uEp6KcLM_EAS-TUE")
        await callback_query.message.answer(
            "Вы уже подписаны на все доступные каналы и чаты!",
            reply_markup=kb.main_russia
        )
    else:
        successful_subscriptions = await check_user_subscriptions_and_add_bonuses(bot, user_id, db)
        if successful_subscriptions:
            subscriptions_list = ", ".join(successful_subscriptions)
            await bot.send_message(callback_query.from_user_id,"CAACAgIAAxkBAAEMIWlmRm_1P-jRYitSrI92MhIHzTApbwACYgMAAm2wQgOZk6ig1YUjNTUE")
            await callback_query.message.answer(
                f"Вы успешно подписаны на: {subscriptions_list}. Бонусы начислены.",
                reply_markup=kb.main_russia
            )
        else:
            await bot.send_message(callback_query.from_user_id,"CAACAgIAAxkBAAEMIWVmRm9Ui6FPUCweVZ4ft21DwCqdLwACcgMAAm2wQgN8hjxqMH187jUE")
            await callback_query.message.answer(
                "Пожалуйста, подпишитесь на все каналы и чаты для получения бонусов.",
                reply_markup=kb.main_russia
            )

    await callback_query.answer()


@router.message(F.text == "💸Presale")
async def presell_ru(message:Message):
    pay_adress = f"UQD9NwqXuJ1MktBwr5tkmVXYM-4dFeNcE3x8R0_KjgxhyP-Y"
    await message.answer(f"To participate in the presale, you need to send a ton to the address\n"f"`{pay_adress}`", reply_markup=kb.main_presell_en, parse_mode="Markdown")

@router.message(F.text == "📲 Connect Wallet")
async def connect(message:Message):
    await message.answer(f"You will be able to connect the wallet a little later", reply_markup=kb.main_english, parse_mode=ParseMode.HTML)
    # await message.answer(f"Connect your wallet to receive bonuses and fully enjoy the game", reply_markup=kb.main_en_connect, parse_mode=ParseMode.HTML)

@router.message(F.text =="⚙️ Profile")
async def profile(message:Message):
    user_id = message.from_user.id
    num_referals = db.count_referals(message.from_user.id)
    bonus = db.get_bonus_points(user_id)
    await message.answer(f"<u>Your profile</u>\n\nID:<b> {message.from_user.id }</b>\nName:<b> {message.from_user.username}</b>\nNumber of referrals: <b> {num_referals}\n</b>Number of bonuses <b> {bonus}</b>", parse_mode=ParseMode.HTML,reply_markup=kb.main_english)

@router.message(F.text =="🤝 Referral Link")
async def referal (message:Message):
    referral_link = f"https://t.me/{cfg.bot_name}?start={message.from_user.id}"
    response_text = (
        "Invite your friends and engage in joint development! For the first 5 invited — 500 bonuses at once, and 100 bonuses for each next one.\n\n"
        "Your referral link:\n"
        f"`{referral_link}`"  # Используем одинарные обратные кавычки для форматирования ссылки как код
    )
    await message.answer(response_text, parse_mode="Markdown", reply_markup=kb.main_english)

@router.message(F.text == "💰 Rewards")
async def show_rewards(message: Message):
    user_id = message.from_user.id
    num_referrals = db.count_referals(user_id)
    bonus_points = db.get_bonus_points(user_id)

    # Подготовка списка каналов с их статусами подписки
    subscription_status = []
    for channel_name, channel_id, _ in CHANNELS:  # Изменили порядок для доступа к имени и ID
        try:
            member = await message.bot.get_chat_member(channel_id, user_id)
            if member.status in ["member", "administrator", "creator"]:
                subscription_status.append(f"✅ - {channel_name} (+50 po)")
            else:
                subscription_status.append(f"❌ - {channel_name} (+50 po)")
        except Exception as e:
            print(f"Error checking channel {channel_name} subscription: {str(e)}")
            subscription_status.append(f"❌ - {channel_name} (+50 po)")  # Assume not subscribed on error

    subscriptions_list = "\n".join(subscription_status)

    await message.answer(
        f"🤝 Invited friends (<b>{num_referrals}/5</b>) (for each +100 points)\n{subscriptions_list}\n You have <b>{bonus_points}</b> bonus points!",
        parse_mode=ParseMode.HTML,
        reply_markup=kb.generate_subscribe_keyboard_en()
    )


@router.message(Command("admin_panel"), F.from_user.id.in_(cfg.ADMINS))
async def admin_panel(message: Message):
    import logging
    logging.info(f"Admin command accessed by {message.from_user.id}")
    await message.answer("Добро пожаловать в админ-панель:", reply_markup=kb.admin)


@router.callback_query(F.data == "admin_analytics")
async def admin_analytics(callback_query: CallbackQuery):
    try:
        stats = db.get_detailed_user_statistics()  # Предполагается, что этот метод возвращает расширенную статистику
        analytics_data = (
            "📊 Аналитика активности пользователей:\n"
            f"Всего пользователей: {stats['total_users']}\n"
            f"Активные пользователи (за последнюю неделю): {stats['active_users']}\n"
            f"Новые пользователи (за последнюю неделю): {stats['new_users']}\n"
            f"Среднее количество бонусов на пользователя: {stats['average_bonus_per_user']:.2f}\n"
            f"Всего бонусов: {stats['total_bonus']}"
        )
        await callback_query.message.edit_text(analytics_data)
    except Exception as e:
        await callback_query.message.edit_text(f"Ошибка при получении аналитики: {str(e)}")
