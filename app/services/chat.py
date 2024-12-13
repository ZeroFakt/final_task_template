from gpt4all import GPT4All
from functools import lru_cache
import logging
import os

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        try:
            # Используем другую модель
            model_name = "orca-mini-3b-gguf2-q4_0.gguf"
            models_directory = "models"
            
            # Создаем директорию для моделей, если её нет
            os.makedirs(models_directory, exist_ok=True)
            
            model_path = os.path.join(models_directory, model_name)
            
            # Инициализация модели
            self.model = GPT4All(
                model_name=model_name,
                model_path=models_directory,
                allow_download=True
            )
            
            # Системный промпт для настройки контекста ЧелГУ
            self.system_prompt = """Ты - помощник Челябинского государственного университета (ЧелГУ).
            Ты должен помогать студентам и абитуриентам, отвечая на их вопросы о университете.
            Отвечай кратко, вежливо и по существу. Если ты не уверен в ответе, так и скажи."""
            
            logger.info(f"Модель успешно загружена: {model_name}")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации модели: {e}")
            raise

    @lru_cache(maxsize=100)
    def get_response(self, user_input: str) -> str:
        try:
            # Формируем полный промпт
            full_prompt = f"{self.system_prompt}\n\nВопрос: {user_input}\nОтвет:"
            
            # Получаем ответ от модели
            response = self.model.generate(
                full_prompt,
                max_tokens=200,
                temp=0.7,
                top_k=40,
                top_p=0.4,
                repeat_penalty=1.18
            )
            
            return response.strip()
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса. Попробуйте переформулировать вопрос."

# Создаем единственный экземпляр сервиса
chat_service = ChatService() 