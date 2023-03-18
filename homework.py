import json
import time
from dotenv import load_dotenv
import os
import telegram
import requests
import logging
from http import HTTPStatus
from exceptions import (IsNot200Error, ApiError,
                        EmptyDictorListError,
                        StatusResponceError,
                        JSONDecoderError)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('pract_token')
TELEGRAM_TOKEN = os.getenv('tg_token')
TELEGRAM_CHAT_ID = os.getenv('chat_id')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s'
)
handler = logging.StreamHandler()


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if not (PRACTICUM_TOKEN or TELEGRAM_TOKEN or TELEGRAM_CHAT_ID):
        message_error = 'Отсутствует важная для работы переменная!!!'
        logger.critical(message_error)
        return False
    return True


def send_message(bot, message):
    """Отправка сообщений."""
    try:
        message_info = f'Сообщение готово к отправке: {message}'
        logger.info(message_info)
        bot.send_message(TELEGRAM_CHAT_ID, message)
        message_info = f'Сообщение отправлено: {message}'
        logger.debug(message_info)
    except Exception:
        message_error = f'Сообщение не удалось отправить: {message}'
        logger.error(message_error)


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    current_timestamp = timestamp
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=params)
        status_code = response.status_code
        if status_code != HTTPStatus.OK:
            message_error = (f'API {ENDPOINT} недоступен, '
                             f'код ошибки {status_code}')
            raise IsNot200Error(message_error)
        return response.json()
    except requests.exceptions.RequestException as error:
        message_error = f'Ошибка в запроссе API: {error}'
        raise ApiError(message_error)
    except json.JSONDecodeError as json_error:
        message_error = f'Ошибка json: {json_error}'
        raise JSONDecoderError(message_error) from json_error


def check_response(response):
    """Проверка валидности полученных данных."""
    if not isinstance(response, dict):
        response_type = type(response)
        message = f'Ответ пришел в неккоректном формате: {response_type}'
        raise TypeError(message)
    if 'homeworks' not in response:
        message = 'В ответе отсутствуют необходимые ключи'
        raise KeyError(message)
    homework = response.get('homeworks')
    if not isinstance(homework, list):
        message = 'Неккоректное значение в ответе у домашней работы'
        raise TypeError(message)
    if homework == []:
        message = 'Домашних работ не обнаружено!'
        raise EmptyDictorListError(message)
    return homework[0]


def parse_status(homework):
    """Проверка статуса задания."""
    if 'homework_name' not in homework:
        message = 'В ответе отсутствуют необходимые ключи'
        raise KeyError(message)
    homework_name = homework['homework_name']
    if 'status' not in homework:
        message = 'В ответе отсутствуют необходимые ключи'
        raise KeyError(message)
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        message_error = f'Пустой статус: {homework_status}'
        raise StatusResponceError(message_error)
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    send_message(bot, 'Бот включен')
    timestamp = int(time.time())
    LAST_ERROR = ''
    last_message = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if homework:
                message = parse_status(homework)
                if message != last_message:
                    last_message = message
                    send_message(bot, message)
            else:
                logger.debug('Нет нового статуса')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != LAST_ERROR:
                LAST_ERROR = message
                send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
