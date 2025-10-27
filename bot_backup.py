"""
Телеграм бот "ФехтНик" для генерации псевдонимов фехтовальщиков
Создано фехтовальщиками для фехтовальщиков от канала: "Не тот Королёв"
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)
from generator import NicknameGenerator

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "8449937753:AAESGwTQbd7t5az7GH9wprVw5i8uuq7Xlmc"

# Состояния для ConversationHandler
(INDIVIDUAL_WEAPON, INDIVIDUAL_GENDER, INDIVIDUAL_STYLE,
 TEAM_WEAPON, TEAM_GENDER, TEAM_STRENGTH) = range(6)

# Инициализируем генератор
generator = NicknameGenerator()

# Брендинг
BRAND_TEXT = '\n\n_Создано фехтовальщиками для фехтовальщиков от канала: "Не тот Королёв"_'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начало работы с ботом - главное меню"""
    keyboard = [
        [InlineKeyboardButton("⚡ Быстрая генерация", callback_data='quick')],
        [InlineKeyboardButton("🎯 Точная генерация", callback_data='individual')],
        [InlineKeyboardButton("👥 Генерация для команды", callback_data='team')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "⚔️ *Добро пожаловать в ФехтНик!* ⚔️\n\n"
        "Я помогу тебе создать уникальный псевдоним и боевой клич "
        "для фехтовальных баталий!\n\n"
        "Выбери режим генерации:"
    ) + BRAND_TEXT
    
    if update.message:
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.callback_query.message.edit_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )


async def quick_generation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Быстрая генерация"""
    query = update.callback_query
    await query.answer()
    
    # Генерируем
    result = generator.generate_quick()
    context.user_data['last_result'] = result
    context.user_data['mode'] = 'quick'
    
    # Формируем ответ (только псевдоним и боевой клич)
    response_text = (
        f"⚔️ *Твой псевдоним:* {result['nickname']}\n\n"
        f"🗣 *Боевой клич:* _{result['battle_cry']}_"
    ) + BRAND_TEXT
    
    # Кнопки после генерации
    keyboard = [
        [InlineKeyboardButton("🔄 Сгенерировать повторно", callback_data='regenerate')],
        [InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')],
        [InlineKeyboardButton("📢 Подписаться на канал", url='https://t.me/netotkorolev')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def start_individual(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало точной генерации - выбор оружия"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🗡 Сабля", callback_data='weapon_сабля')],
        [InlineKeyboardButton("⚔️ Шпага", callback_data='weapon_шпага')],
        [InlineKeyboardButton("🤺 Рапира", callback_data='weapon_рапира')],
        [InlineKeyboardButton("⚔️ Длинный меч", callback_data='weapon_длинный меч')],
        [InlineKeyboardButton("🌟 Световой меч", callback_data='weapon_световой меч')],
        [InlineKeyboardButton("◀️ Назад", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "*Точная генерация*\n\nНа каком оружии ты фехтуешь?" + BRAND_TEXT
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return INDIVIDUAL_WEAPON


async def individual_weapon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора оружия"""
    query = update.callback_query
    await query.answer()
    
    weapon = query.data.replace('weapon_', '')
    context.user_data['weapon'] = weapon
    
    keyboard = [
        [InlineKeyboardButton("👨 Мужчина", callback_data='gender_мужчина')],
        [InlineKeyboardButton("👩 Женщина", callback_data='gender_женщина')],
        [InlineKeyboardButton("◀️ Назад", callback_data='individual')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"*Точная генерация*\n\nОружие: {weapon}\n\nТы мужчина или женщина?" + BRAND_TEXT
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return INDIVIDUAL_GENDER


async def individual_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора пола"""
    query = update.callback_query
    await query.answer()
    
    gender = query.data.replace('gender_', '')
    context.user_data['gender'] = gender
    
    keyboard = [
        [InlineKeyboardButton("💪 Сила", callback_data='style_сила')],
        [InlineKeyboardButton("🦊 Хитрость", callback_data='style_хитрость')],
        [InlineKeyboardButton("🧠 Тактика", callback_data='style_тактика')],
        [InlineKeyboardButton("📚 Опыт", callback_data='style_опыт')],
        [InlineKeyboardButton("🔥 Эмоции", callback_data='style_эмоции')],
        [InlineKeyboardButton("🙏 Фехтовальные боги", callback_data='style_с помощью фехтовальных богов')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_weapon')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    weapon = context.user_data['weapon']
    text = (
        f"*Точная генерация*\n\n"
        f"Оружие: {weapon}\n"
        f"Пол: {gender}\n\n"
        f"За счет чего планируешь побеждать на дорожке?"
    ) + BRAND_TEXT
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return INDIVIDUAL_STYLE


async def individual_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора стиля и генерация результата"""
    query = update.callback_query
    await query.answer()
    
    style = query.data.replace('style_', '')
    weapon = context.user_data['weapon']
    gender = context.user_data['gender']
    
    # Генерируем
    result = generator.generate_individual(weapon, gender, style)
    context.user_data['last_result'] = result
    context.user_data['mode'] = 'individual'
    
    # Формируем ответ
    response_text = (
        f"⚔️ *Твой псевдоним:* {result['nickname']}\n\n"
        f"🗣 *Боевой клич:* _{result['battle_cry']}_\n\n"
        f"🏆 Оружие: {weapon}\n"
        f"👤 Пол: {gender}\n"
        f"💪 Стиль: {style}"
    ) + BRAND_TEXT
    
    # Кнопки после генерации
    keyboard = [
        [InlineKeyboardButton("🔄 Сгенерировать повторно", callback_data='regenerate')],
        [InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')],
        [InlineKeyboardButton("📢 Подписаться на канал", url='https://t.me/netotkorolev')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return ConversationHandler.END


async def start_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало командной генерации - выбор оружия"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🗡 Сабля", callback_data='team_weapon_сабля')],
        [InlineKeyboardButton("⚔️ Шпага", callback_data='team_weapon_шпага')],
        [InlineKeyboardButton("🤺 Рапира", callback_data='team_weapon_рапира')],
        [InlineKeyboardButton("⚔️ Длинный меч", callback_data='team_weapon_длинный меч')],
        [InlineKeyboardButton("🌟 Световой меч", callback_data='team_weapon_световой меч')],
        [InlineKeyboardButton("◀️ Назад", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "*Генерация для команды*\n\nНа каком оружии будет проходить командная встреча?" + BRAND_TEXT
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return TEAM_WEAPON


async def team_weapon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора оружия для команды"""
    query = update.callback_query
    await query.answer()
    
    weapon = query.data.replace('team_weapon_', '')
    context.user_data['team_weapon'] = weapon
    
    keyboard = [
        [InlineKeyboardButton("👨‍👨‍👦 Мужская", callback_data='team_gender_мужская')],
        [InlineKeyboardButton("👩‍👩‍👧 Женская", callback_data='team_gender_женская')],
        [InlineKeyboardButton("◀️ Назад", callback_data='team')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"*Генерация для команды*\n\nОружие: {weapon}\n\nЭто женская команда или мужская?" + BRAND_TEXT
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return TEAM_GENDER


async def team_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора пола команды"""
    query = update.callback_query
    await query.answer()
    
    gender = query.data.replace('team_gender_', '')
    context.user_data['team_gender'] = gender
    
    keyboard = [
        [InlineKeyboardButton("🧠 Тактика", callback_data='team_strength_тактика')],
        [InlineKeyboardButton("📢 Громкий голос", callback_data='team_strength_громкий голос')],
        [InlineKeyboardButton("💪 Сила", callback_data='team_strength_сила')],
        [InlineKeyboardButton("📚 Опыт", callback_data='team_strength_опыт')],
        [InlineKeyboardButton("🔥 Настойчивость", callback_data='team_strength_настойчивость')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_team_weapon')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    weapon = context.user_data['team_weapon']
    text = (
        f"*Генерация для команды*\n\n"
        f"Оружие: {weapon}\n"
        f"Команда: {gender}\n\n"
        f"Какие сильные стороны у участников команды?"
    ) + BRAND_TEXT
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return TEAM_STRENGTH


async def team_strength(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора силы команды и генерация результата"""
    query = update.callback_query
    await query.answer()
    
    strength = query.data.replace('team_strength_', '')
    weapon = context.user_data['team_weapon']
    gender = context.user_data['team_gender']
    
    # Генерируем
    result = generator.generate_team(weapon, gender, strength)
    context.user_data['last_result'] = result
    context.user_data['mode'] = 'team'
    
    # Формируем ответ
    response_text = (
        f"⚔️ *Название команды:* {result['nickname']}\n\n"
        f"🗣 *Боевой клич команды:* _{result['battle_cry']}_\n\n"
        f"🏆 Оружие: {weapon}\n"
        f"👥 Команда: {gender}\n"
        f"💪 Сильная сторона: {strength}"
    ) + BRAND_TEXT
    
    # Кнопки после генерации
    keyboard = [
        [InlineKeyboardButton("🔄 Сгенерировать повторно", callback_data='regenerate')],
        [InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')],
        [InlineKeyboardButton("📢 Подписаться на канал", url='https://t.me/netotkorolev')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return ConversationHandler.END


async def regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторная генерация с теми же параметрами"""
    query = update.callback_query
    await query.answer()
    
    mode = context.user_data.get('mode')
    
    if mode == 'quick':
        result = generator.generate_quick()
        response_text = (
            f"⚔️ *Твой псевдоним:* {result['nickname']}\n\n"
            f"🗣 *Боевой клич:* _{result['battle_cry']}_"
        ) + BRAND_TEXT
    elif mode == 'individual':
        weapon = context.user_data['weapon']
        gender = context.user_data['gender']
        style = context.user_data['last_result']['style']
        result = generator.generate_individual(weapon, gender, style)
        response_text = (
            f"⚔️ *Твой псевдоним:* {result['nickname']}\n\n"
            f"🗣 *Боевой клич:* _{result['battle_cry']}_\n\n"
            f"🏆 Оружие: {weapon}\n"
            f"👤 Пол: {gender}\n"
            f"💪 Стиль: {style}"
        ) + BRAND_TEXT
    elif mode == 'team':
        weapon = context.user_data['team_weapon']
        gender = context.user_data['team_gender']
        strength = context.user_data['last_result']['strength']
        result = generator.generate_team(weapon, gender, strength)
        response_text = (
            f"⚔️ *Название команды:* {result['nickname']}\n\n"
            f"🗣 *Боевой клич команды:* _{result['battle_cry']}_\n\n"
            f"🏆 Оружие: {weapon}\n"
            f"👥 Команда: {gender}\n"
            f"💪 Сильная сторона: {strength}"
        ) + BRAND_TEXT
    else:
        await start(update, context)
        return
    
    context.user_data['last_result'] = result
    
    # Кнопки после генерации
    keyboard = [
        [InlineKeyboardButton("🔄 Сгенерировать повторно", callback_data='regenerate')],
        [InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')],
        [InlineKeyboardButton("📢 Подписаться на канал", url='https://t.me/netotkorolev')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def back_to_weapon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Возврат к выбору оружия"""
    return await start_individual(update, context)


async def back_to_team_weapon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Возврат к выбору оружия для команды"""
    return await start_team(update, context)


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Возврат в главное меню"""
    await start(update, context)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена диалога"""
    await start(update, context)
    return ConversationHandler.END


def main() -> None:
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ConversationHandler для точной генерации
    individual_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_individual, pattern='^individual$')],
        states={
            INDIVIDUAL_WEAPON: [
                CallbackQueryHandler(individual_weapon, pattern='^weapon_'),
                CallbackQueryHandler(main_menu, pattern='^main_menu$'),
            ],
            INDIVIDUAL_GENDER: [
                CallbackQueryHandler(individual_gender, pattern='^gender_'),
                CallbackQueryHandler(start_individual, pattern='^individual$'),
            ],
            INDIVIDUAL_STYLE: [
                CallbackQueryHandler(individual_style, pattern='^style_'),
                CallbackQueryHandler(back_to_weapon, pattern='^back_to_weapon$'),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(main_menu, pattern='^main_menu$'),
            CallbackQueryHandler(cancel, pattern='^cancel$'),
        ],
    )
    
    # ConversationHandler для командной генерации
    team_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_team, pattern='^team$')],
        states={
            TEAM_WEAPON: [
                CallbackQueryHandler(team_weapon, pattern='^team_weapon_'),
                CallbackQueryHandler(main_menu, pattern='^main_menu$'),
            ],
            TEAM_GENDER: [
                CallbackQueryHandler(team_gender, pattern='^team_gender_'),
                CallbackQueryHandler(start_team, pattern='^team$'),
            ],
            TEAM_STRENGTH: [
                CallbackQueryHandler(team_strength, pattern='^team_strength_'),
                CallbackQueryHandler(back_to_team_weapon, pattern='^back_to_team_weapon$'),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(main_menu, pattern='^main_menu$'),
            CallbackQueryHandler(cancel, pattern='^cancel$'),
        ],
    )
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(quick_generation, pattern='^quick$'))
    application.add_handler(CallbackQueryHandler(regenerate, pattern='^regenerate$'))
    application.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu$'))
    application.add_handler(individual_conv_handler)
    application.add_handler(team_conv_handler)
    
    # Запускаем бота
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

