import requests
from bot.config import green_api_config
import logging
import os
import time


# -----------------------------------------------------------------------------------------------------------------------------------
# логи
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f'log_{time.strftime("%Y-%m-%d")}.log')

file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler]
)

def send_message(chat_id, message):
    # получении конфигов в контексте функции
    config = green_api_config()
    # определение эндпоинта куда будет стучать функция с передачей параметров
    url = f"{config['url']}/waInstance{config['id']}/sendMessage/{config['token']}"
    # установка заголовков формата json
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        # для отправки сообщения в личный чат
        'chatId': f'{chat_id}@c.us',
        # отправка в групповой чат
        # 'chatId': f'{chat_id}@g.us',
        "message": message
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if 'idMessage' in response_data:
            logging.info(
                f'Сообщение отправлено к {chat_id}. Message ID: {response_data["idMessage"]}')
            return {'status': 'success', 'idMessage': response_data['idMessage']}
        else:
            logging.error(f'Ошибка при отправке сообщения: {response_data}')
            return {'status': 'error', 'details': response_data}

    except requests.RequestException as Err:
        logging.error(f'[RequestException] в отправке сообщения: {str(Err)}')
        return {'status': 'error', 'details': str(Err)}

# -----------------------------------------------------------------------------------------------------------------------------------
# получить уведомления
def get_notifications():
    config = green_api_config()
    url = f"{config['url']}/waInstance{config['id']}/receiveNotification/{config['token']}"
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logging.info('Уведомления успешно получены')
            return response.json()
        else:
            logging.error('Оишбка при получении уведомлений')
            return {"status": "error", "message": "Unable to fetch notifications"}
    except requests.RequestException as err:
        logging.error(f'[RequestException] в получении уведомлений: {str(err)}')
        return {"status": "error", "details": str(err)}

# -----------------------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------------------
# удалить уведомление
def delete_notification(receiptId):
    config = green_api_config()
    url = f"{config['url']}/waInstance{config['id']}/deleteNotification/{config['token']}/{receiptId}"
    headers = {
        'Content-Type': 'application/json',
    }

    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            logging.info(f'Уведомление {receiptId} успешно удалено')
            return response.json()
        else:
            logging.error(f'Ошибка при удалении уведомления {receiptId}')
            return {"status": "error", "message": "Unable to delete notification"}
    except requests.RequestException as err:
        logging.error(f'[Error] при удалении уведомления: {str(err)}')
        return {"status": "error", "details": str(err)}
    
# -----------------------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------------------
# универсальная функция для отправки файлов (видео, аудио, изображения)
def send_file(chat_id, file_path, file_name=None, caption='', quoted_message_id=None, file_type='image'):
    config = green_api_config()
    url = f"{config['url']}/waInstance{config['id']}/sendFileByUpload/{config['token']}"
    
    mime_types = {
        'image': 'image/jpeg',
        'audio': 'audio/mp3',
        'video': 'video/mp4',
    }
    mime_type = mime_types.get(file_type, 'application/octet-stream')
    
    # проверяет или добавляет расширение файла если оно отсутствует
    # потому что на выходе приходит ссылка на файл без расширения
    if not file_name:
        file_name = f'{file_type}.{mime_type.split("/")[1]}'

    payload = {
        'chatId': f'{chat_id}@c.us',
        'fileName': file_name,
        'caption': caption,
        'quotedMessageId': quoted_message_id or ''
    }
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (file_name, file, mime_type)}
            response = requests.post(url, data=payload, files=files)
            response.raise_for_status()
            response_data = response.json()


            if 'idMessage' in response_data:
                logging.info(f'Файл отправлен к {chat_id}. Message ID: {response_data["idMessage"]}')
                return {'status': 'success', 'idMessage': response_data['idMessage']}
            else:
                logging.error(f'Ошибка при отправке файла: {response_data}')
                return {'status': 'error', 'details': response_data}
            
    except requests.exceptions.HTTPError as Err:
        logging.error(f'[HTTPError] при отправке файла: {str(Err)}')
        return {"status": "error", "details": f"[HTTPError]: {str(Err)}"}
    except requests.RequestException as Err:
        logging.error(f'[RequestException] при отправке файла: {str(Err)}')
        return {"status": "error", "details": f"[RequestException]: {str(Err)}"}
    except Exception as Err:
        logging.error(f'[Error] при отправке файла: {str(Err)}')
        return {"status": "error", "details": f"[Error]: {str(Err)}"}

# -----------------------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------------------
# локация
def send_location(chat_id, name_location, address, latitude, longitude):
    config = green_api_config()
    url = f"{config['url']}/waInstance{config['id']}/sendLocation/{config['token']}"
    payload = {
        "chatId": f"{chat_id}@c.us",
        "nameLocation": name_location,
        "address": address,
        "latitude": latitude,
        "longitude": longitude
    }
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        response_data = response.json()

        if 'idMessage' in response_data:
            logging.info(f'Геолокация отправлена к {chat_id}. Расположение: {name_location}')
            return {'status': 'success', 'idMessage': response_data['idMessage']}
        else:
            logging.error(f'Ошибка при отправке местоположения: {response_data}')
            return {'status': 'error', 'details': response_data}

    except requests.exceptions.HTTPError as Err:
        logging.error(f'[HTTPError] в отправке местоположения: {str(Err)}')
        return {"status": "error", "details": f"[HTTPError]: {str(Err)}"}

    except requests.RequestException as Err:
        logging.error(f'[RequestException] в отправке местоположения: {str(Err)}')
        return {"status": "error", "details": f"[RequestException]: {str(Err)}"}