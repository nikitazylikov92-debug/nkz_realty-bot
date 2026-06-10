import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from anthropic import Anthropic

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Клиент Anthropic
anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# База ЖК — сюда добавляй свои объекты
REALTY_DATABASE = """
1. ЖК Крылатская 33, застройщик Сзади Сияние
   - Скидки 30% на студии при ипотеке и полной оплате
   - Цены: от 16 млн ₽
   - Подходит: любителям Крылатского, парков, семейная ипотека
   - Риск: много студий → высокая конкуренция в аренде/перепродаже
   - Низкая распроданность → хорошая скидка сейчас

2. ЖК Союз, застройщик Родина
   - Скидки до 13% при полной оплате или ипотеке
   - Цены: студии от 17,5 млн, 1к от 21 млн, 2к от 30 млн
   - Ключи: декабрь (скоро!)
   - Подходит: кто хочет ключи быстро, любит спорт (инфраструктура внутри ЖК)

3. ЖК ВЕЕР, МР Групп
   - Акция до 15 июня: 36,8 м² за 17,7 млн ₽
   - Рассрочка: 20% ПВ + 100 тыс./мес на 3 года (цена от 20 млн)
   - Ипотека или полная оплата тоже доступны
   - Перспектива: КРТ + метро, горизонт 5 лет
   - Потенциал роста: один из самых высоких в базе

4. ЖК Новые Ватутинки, квартал у реки
   - Скидки до 15% на выделенные лоты
   - Цены: от 7,6 млн ₽
   - Семейная ипотека: отлично подходит
   - Рядом: метро скоро (ст. Десна и Ватутинки к 2029), река Десна, парк Андерсен
   - Инфраструктура: 3 школы, 5 садов, поликлиника, ТЦ, база ЦСКА
   - Подходит: семьям с детьми, инвестиция с прицелом на метро

5. Квартал Герцена и Метроном
   - Ипотечная ставка 6% для всех на 2 года (без удорожания)
   - ПВ: 20–30%
   - Один из самых качественных застройщиков
   - Подходит: кто хочет новостройку без искусственного удорожания

6. Аквилон Би Сайд
   - Студии с 2 окнами, ПВ от 3 млн, небольшие ежемесячные платежи
   - Инвест-стратегия: купить → отделка → сдать
   - Близость к метро → высокая арендная ставка

7. Обручева 30
   - Однушка за 20 млн
   - Рассрочка: 50% ПВ + 50 тыс./мес, остаток в апреле 2027, ключи после
   - Хорошо для аренды и перепродажи через 4 года
   - Минус: застройщик сдаёт некачественно

8. ЖК Эра, Tekta (Павелецкая)
   - Премиум-класс
   - 2-я очередь: 1к от 26 млн, ПВ 30% + 250 тыс./мес
   - 1-я очередь: 1к от 30 млн (инвестор защищён от демпинга)
   - Подходит: инвесторам в премиум-сегмент

9. Пейв
   - Тихая Москва в центре
   - 1к от 20 млн (семейная ипотека) или от 25 млн
   - Рассрочка: 30% ПВ + 0,5%/мес + 10% раз в год, срок 2 года
   - Стратегия: семейная ипотека → переуступка через 2 года
"""

# Системный промпт риелтора
SYSTEM_PROMPT = f"""Ты — профессиональный риелтор-консультант. Твоя задача — помогать клиентам подобрать квартиру из базы ЖК.

БАЗА ЖК (используй только эти варианты):
{REALTY_DATABASE}

ПРАВИЛА РАБОТЫ:
1. Всегда начинай с уточняющих вопросов: бюджет, цель (жить/инвестиция/ребёнку), тип квартиры, наличие детей для семейной ипотеки, первоначальный взнос
2. Предлагай 2–3 варианта максимум, объясняй ПОЧЕМУ именно они подходят
3. Считай примерные платежи по ипотеке если нужно (семейная ипотека 6%, рыночная ~20%)
4. Будь дружелюбным, говори простым языком, без занудства
5. Если клиент хочет подробности о районе — рассказывай об инфраструктуре, транспорте, перспективах
6. Не придумывай ЖК, которых нет в базе
7. Общайся на русском языке
8. Если клиент готов к сделке — предложи связаться с менеджером

ВАЖНО: Ты умный живой риелтор, не робот. Не перечисляй все ЖК сразу — веди диалог, задавай вопросы, подбирай персонально.
"""

# Хранилище истории диалогов (в памяти)
conversation_history = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user_id = update.effective_user.id
    conversation_history[user_id] = []  # сброс истории

    await update.message.reply_text(
        "👋 Привет! Я риелтор-консультант.\n\n"
        "Помогу подобрать квартиру в новостройке Москвы под ваш бюджет и цели.\n\n"
        "Расскажите — что ищете? Для себя или как инвестицию? "
        "Какой примерный бюджет? 🏠"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс диалога командой /reset"""
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text(
        "🔄 Начнём сначала! Расскажите, что ищете?"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка входящих сообщений"""
    user_id = update.effective_user.id
    user_message = update.message.text

    # Инициализация истории если нет
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Добавляем сообщение пользователя в историю
    conversation_history[user_id].append({
        "role": "user",
        "content": user_message
    })

    # Показываем индикатор набора текста
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    try:
        # Запрос к Claude
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=conversation_history[user_id]
        )

        assistant_message = response.content[0].text

        # Сохраняем ответ в историю
        conversation_history[user_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        # Ограничиваем историю последними 20 сообщениями (экономия токенов)
        if len(conversation_history[user_id]) > 20:
            conversation_history[user_id] = conversation_history[user_id][-20:]

        await update.message.reply_text(assistant_message)

    except Exception as e:
        logger.error(f"Ошибка при обращении к Claude: {e}")
        await update.message.reply_text(
            "😔 Что-то пошло не так. Попробуйте ещё раз или напишите /reset"
        )


def main():
    """Запуск бота"""
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        raise ValueError("Не задан TELEGRAM_BOT_TOKEN!")

    app = Application.builder().token(telegram_token).build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
