"""
Телеграм бот "ФехтНик" для генерации псевдонимов фехтовальщиков
Оптимизированная версия с обработкой ошибок и улучшенной производительностью
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
from telegram.error import TelegramError, NetworkError, TimedOut
from httpx import Timeout
from generator import NicknameGenerator
from config import (
    BOT_TOKEN, BRAND_TEXT, CHANNEL_URL,
    INDIVIDUAL_WEAPON, INDIVIDUAL_GENDER, INDIVIDUAL_STYLE,
    TEAM_WEAPON, TEAM_GENDER, TEAM_STRENGTH,
    REQUEST_TIMEOUT, CONNECTION_POOL_SIZE, CONNECT_TIMEOUT, READ_TIMEOUT
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализируем генератор один раз
generator = NicknameGenerator()

# Константы для кнопок (создаем один раз)
ACTION_BUTTONS = [
    [InlineKeyboardButton("🔄 Сгенерировать повторно", callback_data='regenerate')],
    [InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')],
    [InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_URL)],
]
ACTION_MARKUP = InlineKeyboardMarkup(ACTION_BUTTONS)


def create_weapon_keyboard(prefix=''):
    """Создание клавиатуры для выбора оружия"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗡 Сабля", callback_data=f'{prefix}weapon_сабля')],
        [InlineKeyboardButton("⚔️ Шпага", callback_data=f'{prefix}weapon_шпага')],
        [InlineKeyboardButton("🤺 Рапира", callback_data=f'{prefix}weapon_рапира')],
        [InlineKeyboardButton("⚔️ Длинный меч", callback_data=f'{prefix}weapon_длинный меч')],
        [InlineKeyboardButton("🌟 Световой меч", callback_data=f'{prefix}weapon_световой меч')],
        [InlineKeyboardButton("◀️ Назад", callback_data='main_menu')],
    ])


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Глобальный обработчик ошибок"""
    logger.error(f"Ошибка при обработке обновления: {context.error}", exc_info=context.error)
    
    # Пытаемся уведомить пользователя
    try:
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "😔 Произошла ошибка. Попробуйте /start для перезапуска бота."
            )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение об ошибке: {e}")


async def safe_edit_message(query, text, reply_markup, parse_mode='Markdown'):
    """Безопасное редактирование сообщения с обработкой ошибок"""
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except TelegramError as e:
        logger.warning(f"Не удалось отредактировать сообщение: {e}")
        # Если редактирование не удалось, отправляем новое сообщение
        await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)


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
    
    try:
        if update.message:
            await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await safe_edit_message(update.callback_query, welcome_text, reply_markup)
    except TelegramError as e:
        logger.error(f"Ошибка в start: {e}")


async def quick_generation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Быстрая генерация"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Генерируем
        result = generator.generate_quick()
        context.user_data['last_result'] = result
        context.user_data['mode'] = 'quick'
        
        # Формируем ответ
        response_text = (
            f"⚔️ *Твой псевдоним:* {result['nickname']}\n\n"
            f"🗣 *Боевой клич:* _{result['battle_cry']}_"
        ) + BRAND_TEXT
        
        await safe_edit_message(query, response_text, ACTION_MARKUP)
    except Exception as e:
        logger.error(f"Ошибка в quick_generation: {e}")
        await query.message.reply_text("Произошла ошибка при генерации. Попробуйте еще раз.")


async def start_individual(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало точной генерации - выбор оружия"""
    query = update.callback_query
    await query.answer()
    
    text = "*Точная генерация*\n\nНа каком оружии ты фехтуешь?" + BRAND_TEXT
    await safe_edit_message(query, text, create_weapon_keyboard())
    
    return INDIVIDUAL_WEAPON


async def individual_weapon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора оружия"""
    query = update.callback_query
    await query.answer()
    
    weapon = query.data.replace('weapon_', '')
    context.user_data['weapon'] = weapon
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨 Мужчина", callback_data='gender_мужчина')],
        [InlineKeyboardButton("👩 Женщина", callback_data='gender_женщина')],
        [InlineKeyboardButton("◀️ Назад", callback_data='individual')],
    ])
    
    text = f"*Точная генерация*\n\nОружие: {weapon}\n\nТы мужчина или женщина?" + BRAND_TEXT
    await safe_edit_message(query, text, keyboard)
    
    return INDIVIDUAL_GENDER


async def individual_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора пола"""
    query = update.callback_query
    await query.answer()
    
    gender = query.data.replace('gender_', '')
    context.user_data['gender'] = gender
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💪 Сила", callback_data='style_сила')],
        [InlineKeyboardButton("🦊 Хитрость", callback_data='style_хитрость')],
        [InlineKeyboardButton("🧠 Тактика", callback_data='style_тактика')],
        [InlineKeyboardButton("📚 Опыт", callback_data='style_опыт')],
        [InlineKeyboardButton("🔥 Эмоции", callback_data='style_эмоции')],
        [InlineKeyboardButton("🙏 Фехтовальные боги", callback_data='style_с помощью фехтовальных богов')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_weapon')],
    ])
    
    weapon = context.user_data['weapon']
    text = (
        f"*Точная генерация*\n\n"
        f"Оружие: {weapon}\n"
        f"Пол: {gender}\n\n"
        f"За счет чего планируешь побеждать на дорожке?"
    ) + BRAND_TEXT
    
    await safe_edit_message(query, text, keyboard)
    return INDIVIDUAL_STYLE


async def individual_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора стиля и генерация результата"""
    query = update.callback_query
    await query.answer()
    
    try:
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
        
        await safe_edit_message(query, response_text, ACTION_MARKUP)
    except Exception as e:
        logger.error(f"Ошибка в individual_style: {e}")
        await query.message.reply_text("Произошла ошибка при генерации. Попробуйте еще раз.")
    
    return ConversationHandler.END


async def start_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало командной генерации - выбор оружия"""
    query = update.callback_query
    await query.answer()
    
    text = "*Генерация для команды*\n\nНа каком оружии будет проходить командная встреча?" + BRAND_TEXT
    await safe_edit_message(query, text, create_weapon_keyboard('team_'))
    
    return TEAM_WEAPON


async def team_weapon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора оружия для команды"""
    query = update.callback_query
    await query.answer()
    
    weapon = query.data.replace('team_weapon_', '')
    context.user_data['team_weapon'] = weapon
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍👨‍👦 Мужская", callback_data='team_gender_мужская')],
        [InlineKeyboardButton("👩‍👩‍👧 Женская", callback_data='team_gender_женская')],
        [InlineKeyboardButton("◀️ Назад", callback_data='team')],
    ])
    
    text = f"*Генерация для команды*\n\nОружие: {weapon}\n\nЭто женская команда или мужская?" + BRAND_TEXT
    await safe_edit_message(query, text, keyboard)
    
    return TEAM_GENDER


async def team_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора пола команды"""
    query = update.callback_query
    await query.answer()
    
    gender = query.data.replace('team_gender_', '')
    context.user_data['team_gender'] = gender
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧠 Тактика", callback_data='team_strength_тактика')],
        [InlineKeyboardButton("📢 Громкий голос", callback_data='team_strength_громкий голос')],
        [InlineKeyboardButton("💪 Сила", callback_data='team_strength_сила')],
        [InlineKeyboardButton("📚 Опыт", callback_data='team_strength_опыт')],
        [InlineKeyboardButton("🔥 Настойчивость", callback_data='team_strength_настойчивость')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_team_weapon')],
    ])
    
    weapon = context.user_data['team_weapon']
    text = (
        f"*Генерация для команды*\n\n"
        f"Оружие: {weapon}\n"
        f"Команда: {gender}\n\n"
        f"Какие сильные стороны у участников команды?"
    ) + BRAND_TEXT
    
    await safe_edit_message(query, text, keyboard)
    return TEAM_STRENGTH


async def team_strength(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора силы команды и генерация результата"""
    query = update.callback_query
    await query.answer()
    
    try:
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
        
        await safe_edit_message(query, response_text, ACTION_MARKUP)
    except Exception as e:
        logger.error(f"Ошибка в team_strength: {e}")
        await query.message.reply_text("Произошла ошибка при генерации. Попробуйте еще раз.")
    
    return ConversationHandler.END


async def regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторная генерация с теми же параметрами"""
    query = update.callback_query
    await query.answer()
    
    try:
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
        await safe_edit_message(query, response_text, ACTION_MARKUP)
    except Exception as e:
        logger.error(f"Ошибка в regenerate: {e}")
        await query.message.reply_text("Произошла ошибка при генерации. Попробуйте еще раз.")


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
    try:
        # Создаем приложение с оптимизированными настройками
        application = (
            Application.builder()
            .token(BOT_TOKEN)
            .connect_timeout(CONNECT_TIMEOUT)
            .read_timeout(READ_TIMEOUT)
            .write_timeout(REQUEST_TIMEOUT)
            .pool_timeout(REQUEST_TIMEOUT)
            .connection_pool_size(CONNECTION_POOL_SIZE)
            .build()
        )
        
        # Добавляем глобальный обработчик ошибок
        application.add_error_handler(error_handler)
        
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
        logger.info("🚀 Бот запущен (оптимизированная версия)!")
        application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
        raise


if __name__ == '__main__':
    main()

