import logging
import os
from telegram import Update, Voice
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import grpc
import synthesis_pb2
import synthesis_pb2_grpc

# Получение конфигурационных данных из переменных окружения
SMARTSPEECH_HOST = 'smartspeech.sber.ru'
SMARTSPEECH_TOKEN = os.getenv('SMARTSPEECH_TOKEN')
SMARTSPEECH_CA = os.getenv('SMARTSPEECH_CA')  # Путь к файлу CA-сертификата (если требуется)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Настройка логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация клиента gRPC
def get_smartspeech_client():
    try:
        ssl_cred = grpc.ssl_channel_credentials(
            root_certificates=open(SMARTSPEECH_CA, 'rb').read() if SMARTSPEECH_CA else None
        )
    except IOError as e:
        logger.error(f'Error reading CA certificate: {e}')
        raise
    token_cred = grpc.access_token_call_credentials(SMARTSPEECH_TOKEN)
    channel = grpc.secure_channel(SMARTSPEECH_HOST, grpc.composite_channel_credentials(ssl_cred, token_cred))
    return synthesis_pb2_grpc.SmartSpeechStub(channel)

# Обработчик команды /start
def start(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Привет! Отправь мне текстовое сообщение, и я синтезирую речь для тебя.')

# Обработчик текстовых сообщений
def text_message(update: Update, context):
    # Получение текста сообщения пользователя
    user_text = update.message.text
    audio_file_path = 'audio_response.wav'

    try:
        # Создание запроса на синтез речи
        synthesis_request = synthesis_pb2.SynthesisRequest()
        synthesis_request.text = user_text

        # Вызов сервиса SmartSpeech для синтеза речи
        with grpc.secure_channel(SMARTSPEECH_HOST, grpc.composite_channel_credentials(ssl_cred, token_cred)) as channel:
            smartspeech_client = synthesis_pb2_grpc.SmartSpeechStub(channel)
            response = smartspeech_client.Synthesize(synthesis_request)

            # Сохранение голосового ответа в файл
            with open(audio_file_path, 'wb') as audio_file:
               for audio_chunk in response:
                    audio_file.write(audio_chunk.data)

            # Отправка голосового ответа пользователю
            context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(audio_file_path, 'rb'))
    except Exception as e:
        logger.error(f'Error during speech synthesis: {e}')

# Главная функция для запуска бота
def main():
    # Инициализация Telegram-бота
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Добавление обработчиков команд и сообщений
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_message))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
