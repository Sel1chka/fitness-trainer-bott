import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)
from programs import get_program_by_goal

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токен из переменных окружения
TOKEN = os.environ.get('BOT_TOKEN')

# Состояния для диалога
ASK_GOAL, ASK_LEVEL = range(2)

# Вопросы для пользователя
GOALS = {
    "weight_loss": "Сжигание жира",
    "muscle_gain": "Набор массы", 
    "strength": "Сила",
    "endurance": "Выносливость"
}

LEVELS = {
    "beginner": "Новичок",
    "intermediate": "Средний", 
    "advanced": "Продвинутый"
}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я помогу тебе создать индивидуальную программу тренировок.\n\n"
        "Нажми /create чтобы начать подбор программы."
    )

# Команда /create - начало создания программы
async def create_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем клавиатуру с целями
    keyboard = [[KeyboardButton(goal)] for goal in GOALS.values()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "🎯 Выбери свою основную цель:",
        reply_markup=reply_markup
    )
    return ASK_GOAL

# Обработка выбора цели
async def handle_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chosen_goal = update.message.text
    
    # Находим ключ цели по русскому названию
    goal_key = None
    for key, value in GOALS.items():
        if value == chosen_goal:
            goal_key = key
            break
    
    if goal_key:
        context.user_data['goal'] = goal_key
        
        # Спрашиваем уровень подготовки
        keyboard = [[KeyboardButton(level)] for level in LEVELS.values()]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "📊 Твой уровень подготовки:",
            reply_markup=reply_markup
        )
        return ASK_LEVEL
    else:
        await update.message.reply_text("Пожалуйста, выбери цель из списка")
        return ASK_GOAL

# Обработка выбора уровня и создание программы
async def handle_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chosen_level = update.message.text
    
    # Находим ключ уровня
    level_key = None
    for key, value in LEVELS.items():
        if value == chosen_level:
            level_key = key
            break
    
    if level_key:
        goal = context.user_data.get('goal')
        
        # Получаем программу
        program = get_program_by_goal(goal, level_key)
        
        # Формируем текст программы
        program_text = f"""
🎉 ТВОЯ ПРОГРАММА ГОТОВА!

📋 {program['title']}
{program['description']}

✨ ОСОБЕННОСТИ:
"""
        for feature in program['features']:
            program_text += f"• {feature}\n"
        
        program_text += "\n📅 **РАСПИСАНИЕ НА НЕДЕЛЮ:**\n"
        for day, workout in program['weekly_schedule'].items():
            program_text += f"• {day}: {workout}\n"
        
        program_text += f"""
🥗 ПИТАНИЕ:
{program['nutrition']}

💧 ВОДНЫЙ РЕЖИМ:
{program['water']}

💡 СОВЕТ:
{program.get('tips', 'Слушай свой организм и отдыхай!')}

Чтобы создать новую программу, нажми /create
"""
        
        await update.message.reply_text(program_text, parse_mode='Markdown')
        await update.message.reply_text(
            "Удачных тренировок! 💪",
            reply_markup=ReplyKeyboardMarkup.remove_keyboard()
        )
        
        # Очищаем данные пользователя
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text("Пожалуйста, выбери уровень из списка")
        return ASK_LEVEL

# Отмена
