from bot import create_app
import threading
import time
from bot.services import process_ai


app = create_app()

# функция с бесконечными ответами AI
def periodic_answer(interval):
    # управление контекстом
    with app.app_context():
        while True:
            process_ai()
            time.sleep(interval)

# для автоматических ответов 
# if __name__ == "__main__":
#     host = '127.0.0.1'
#     port = 4042
#     print(f"Server on http://{host}:{port}")
#     # Интервал 3 минуты
#     interval = 180
#     threading.Thread(target=periodic_answer, args=(interval,), daemon=True).start()

#     app.run(debug=True, host=host, port=port)

if __name__ == "__main__":
    host = '127.0.0.1'
    port = 4042
    print(f"Server on http://{host}:{port}")
    app.run(debug=True, host=host, port=port)