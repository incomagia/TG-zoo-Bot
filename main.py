from telegram.ext import ApplicationBuilder
from handlers import setup_handlers
import logging

# ВСТАВЬ СЮДА СВОЙ ТОКЕН ОТ BotFather
BOT_TOKEN = "7550440515:AAFQMO9mDenJoaUDoIn_eg8yDWntP_JbLMc"

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Подключаем все обработчики
    setup_handlers(app)

    # Запускаем бота
    app.run_polling()

if __name__ == "__main__":
    main()
