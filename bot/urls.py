from flask import Blueprint, request, jsonify
import os
import time
import logging
from flask_cors import cross_origin
from .models import Message, Location
from . import db
from .services import (
    send_message,
    get_details_notifications,
    get_fields_notifications,
    delete_notification,
    send_file,
    send_location,
)

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


bot = Blueprint('main', __name__)

# -----------------------------------------------------------------------------------------------------------------------------------
# отправка сообщений
@bot.route('/send_message', methods=['POST'])
@cross_origin()
def send_message_route():
    data = request.json
    chat_id = data.get('chatId')
    message = data.get('message')

    if not chat_id or not message:
        logging.error(f"Отсутствуют обязательные поля: chatId={chat_id}, message={message}")
        return jsonify({"error": "Отсутствуют обязательные поля: chatId, message"}), 400

    if len(chat_id) < 10:
        logging.error(f"chatId слишком короткий: {chat_id}")
        return jsonify({"error": "chatId должен содержать не менее 10 символов"}), 400

    try:
        result = send_message(chat_id, message)
        if result.get('status') == 'success':
            new_message = Message(
                chat_id=chat_id,
                content=message
            )
            db.session.add(new_message)
            db.session.commit()
            logging.info(f"Сообщение успешно отправлено: chatId={chat_id}")
            return jsonify(result), 200
        else:
            logging.error(f"Ошибка при отправке сообщения: {result}")
            return jsonify({"Error": "Данные удалось сохранить в базу данных", "details": result}), 500
    except Exception as Err:
        logging.error(f"Исключение: {str(Err)}")
        return jsonify({"Error": str(Err)}), 500 

# -----------------------------------------------------------------------------------------------------------------------------------
# получение уведомлений
@bot.route('/notifications_details', methods=['GET'])
def receive_notifications_details_route():
    try:
        notifications = get_details_notifications()

        if notifications is None:
            logging.error("Получены некорректные данные: notifications равен None")
            print('Получены некорректные данные: notifications равен None')
            return jsonify({"status": "error", "message": "No notifications available"}), 204
        
        if notifications.get('status') == 'error':
            logging.error(f"Ошибка при получении уведомлений: {notifications.get('message')}")
            return jsonify(notifications), 500
        
        logging.info("Получены уведомления")
        return jsonify(notifications), 200

    except Exception as Err:
        logging.error(f"Ошибка в receive_notifications_details_route: {Err}")
        return jsonify({"error": "Ошибка при получении уведомлений"}), 500

# -----------------------------------------------------------------------------------------------------------------------------------
# удаление уведомлений
@bot.route('/notifications/<int:receiptId>', methods=['DELETE'])
def remove_notification_route(receiptId):
    try:
        result = delete_notification(receiptId)
        
        if result.get('status') == 'error':
            logging.error(f"Ошибка при удалении уведомления с id={receiptId}: {result.get('message')}")
            return jsonify(result), 500
        
        logging.info(f"Уведомление с id={receiptId} успешно удалено")
        return jsonify(result), 200
    
    except Exception as Err:
        logging.error(f"Ошибка в remove_notification_route при удалении уведомления с id={receiptId}: {Err}")
        return jsonify({"error": "Ошибка при удалении уведомления"}), 500
    
# -----------------------------------------------------------------------------------------------------------------------------------
#* [AI] версия
@bot.route('/notifications', methods=['GET'])
def receive_notifications_route():
    try:
        message_text, chat_id = get_fields_notifications()

        if message_text is None or chat_id is None:
            logging.error("Ошибка при получении уведомлений")
            return jsonify({"status": "error", "message": "Unable to fetch notifications"}), 500

        logging.info("Получены уведомления")
        return jsonify({"message": message_text, "chatId": chat_id}), 200

    except Exception as Err:
        logging.error(f"Ошибка в receive_notifications_route: {Err}")
        return jsonify({"error": "Ошибка при получении уведомлений"}), 500

# -----------------------------------------------------------------------------------------------------------------------------------
#! необязателен к использованию
#todo: в файле main.py функция process_ai() запускается каждые 3 минуты (20 запросов в час)
#* [AI] формирование ответа
# @bot.route('/process', methods=['POST'])
# def process():
#     process_ai()
#     return jsonify({'status': 'success'})

# -----------------------------------------------------------------------------------------------------------------------------------
# отправить файл
@bot.route('/send_media', methods=['POST'])
@cross_origin()
def send_media_route():
    chat_id = request.form.get('chatId')
    file = request.files.get('file')
    caption = request.form.get('caption', '')
    file_name = request.form.get('fileName', '')
    media_type = request.form.get('mediaType')
    quoted_message_id = request.form.get('quotedMessageId', None)

    if not chat_id or not file or not media_type:
        logging.error(f"Обязательные поля для отправки медиа: chatId={chat_id}, mediaType={media_type}")
        return jsonify({"error": "Missing required fields"}), 400

    if media_type == 'image':
        file_path = f'content/images/{file.filename}'
    elif media_type == 'audio':
        file_path = f'content/audio/{file.filename}'
    elif media_type == 'video':
        file_path = f'content/video/{file.filename}'
    else:
        logging.error(f"Неподдерживаемый тип медиа: {media_type}")
        return jsonify({"error": "Unsupported media type"}), 400

    try:
        file.save(file_path)
        logging.info(f"Файл сохранен: {file_path}")

        result = send_file(
            chat_id, 
            file_path, 
            file_name or file.filename, 
            caption, 
            quoted_message_id, 
            media_type
        )
        if result.get('status') == 'success':
            logging.info(f"Файл успешно отправлен: {result}")
            # удаление файла после успешной отправки чтобы не нагружать память сервера
            os.remove(file_path)
            return jsonify(result), 200
        else:
            logging.error(f"Ошибка при отправке файла: {result}")
            return jsonify(result), 500

    except Exception as Err:
        logging.error(f"Ошибка при сохранении или отправке файла: {Err}")
        return jsonify({"error": "Ошибка при обработке файла"}), 500

# -----------------------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------------------
# отправить локацию
@bot.route('/send_location', methods=['POST'])
@cross_origin()
def send_location_route():
    data = request.get_json()
    chat_id = data.get('chatId')
    name_location = data.get('nameLocation')
    address = data.get('address')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not chat_id or not name_location or not address or not latitude or not longitude:
        logging.error(f"Отсутствуют обязательные поля для отправки локации: chatId={chat_id}")
        return jsonify({"error": "Missing required fields"}), 400

    result = send_location(chat_id, name_location, address, latitude, longitude)

    if result.get('status') == 'success':
        new_location = Location(
            chat_id=chat_id,
            name_location=name_location,
            address=address,
            latitude=float(latitude),
            longitude=float(longitude)
        )
        db.session.add(new_location)
        db.session.commit()
        logging.info(f"Локация успешно отправлена: chatId={chat_id}")
        return jsonify(result), 200
    else:
        logging.error(f"Ошибка отправки локации: {result}")
        return jsonify(result), 500 if result.get('status') == 'error' else 400