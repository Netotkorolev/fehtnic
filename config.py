"""
Конфигурационный файл для бота ФехтНик
"""

# Токен бота
BOT_TOKEN = "8449937753:AAESGwTQbd7t5az7GH9wprVw5i8uuq7Xlmc"

# Брендинг
BRAND_TEXT = '\n\n_Создано фехтовальщиками для фехтовальщиков от канала: "Не тот Королёв"_'
CHANNEL_URL = 'https://t.me/netotkorolev'

# Состояния для ConversationHandler
(INDIVIDUAL_WEAPON, INDIVIDUAL_GENDER, INDIVIDUAL_STYLE,
 TEAM_WEAPON, TEAM_GENDER, TEAM_STRENGTH) = range(6)

# Настройки приложения
REQUEST_TIMEOUT = 30  # Таймаут для HTTP запросов в секундах
CONNECTION_POOL_SIZE = 8  # Размер пула соединений
CONNECT_TIMEOUT = 10  # Таймаут подключения
READ_TIMEOUT = 10  # Таймаут чтения

