import logging
from datetime import datetime
from typing import Optional, Tuple
import re
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


class CommandProcessor:
    def __init__(self):
        self.predefined_commands = {
            "привет джарвис": self.greeting_command,
            "hello jarvis": self.greeting_command,
            "какое время": self.time_command,
            "what time": self.time_command,
            "включить свет": self.light_on_command,
            "turn on light": self.light_on_command,
            "выключить свет": self.light_off_command,
            "turn off light": self.light_off_command,
            "какая погода": self.weather_command,
            "what's the weather": self.weather_command,
            "выключись": self.shutdown_command,
            "стоп": self.shutdown_command,
            "stop": self.shutdown_command,
            "shutdown": self.shutdown_command,
        }
        
        self.reminders = []
    
    async def process_command(self, text: str) -> Tuple[str, str]:
        text_lower = text.lower().strip()
        
        logger.info(f"Processing command: {text_lower}")
        
        for command_pattern, handler in self.predefined_commands.items():
            if command_pattern in text_lower:
                response = await handler(text)
                return response, "predefined"
        
        if "напомни" in text_lower or "remind me" in text_lower:
            response = await self.reminder_command(text)
            return response, "predefined"
        
        return "", "gpt"
    
    async def greeting_command(self, text: str) -> str:
        greetings = [
            "Здравствуйте, сэр. Чем могу помочь?",
            "Приветствую вас. Готов к работе.",
            "Добрый день. Жду ваших указаний.",
            "Всегда к вашим услугам, сэр."
        ]
        import random
        return random.choice(greetings)
    
    async def time_command(self, text: str) -> str:
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        
        if "ru" in text.lower() or any(c in text for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"):
            return f"Сейчас {time_str}"
        else:
            return f"It's {time_str}"
    
    async def light_on_command(self, text: str) -> str:
        logger.info("Light ON command executed")
        responses = [
            "Свет включён, сэр.",
            "Освещение активировано.",
            "Конечно, включаю свет."
        ]
        import random
        return random.choice(responses)
    
    async def light_off_command(self, text: str) -> str:
        logger.info("Light OFF command executed")
        responses = [
            "Свет выключен, сэр.",
            "Освещение деактивировано.",
            "Выключаю свет."
        ]
        import random
        return random.choice(responses)
    
    async def weather_command(self, text: str) -> str:
        from backend.config import settings
        
        if not settings.OPENWEATHERMAP_API_KEY:
            return "К сожалению, API ключ для получения погоды не настроен."
        
        try:
            city = "Moscow"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.OPENWEATHERMAP_API_KEY}&units=metric&lang=ru"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        temp = data["main"]["temp"]
                        description = data["weather"][0]["description"]
                        return f"Сейчас в Москве {temp:.1f} градусов, {description}."
                    else:
                        return "Не удалось получить данные о погоде."
        except asyncio.TimeoutError:
            return "Превышено время ожидания при получении данных о погоде."
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return "Произошла ошибка при получении информации о погоде."
    
    async def reminder_command(self, text: str) -> str:
        reminder_text = re.sub(r"(напомни|remind me|мне|о|about)", "", text, flags=re.IGNORECASE).strip()
        
        if reminder_text:
            self.reminders.append({
                "text": reminder_text,
                "created_at": datetime.now()
            })
            return f"Хорошо, я напомню вам о: {reminder_text}"
        else:
            return "Извините, я не понял, о чём вам напомнить."
    
    async def shutdown_command(self, text: str) -> str:
        return "До свидания, сэр. Перехожу в режим ожидания."
    
    def get_reminders(self) -> list:
        return self.reminders
