import logging
from openai import OpenAI
from typing import Optional, List, Dict
from backend.config import settings

logger = logging.getLogger(__name__)


class LLMHandler:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.GPT_MODEL
        self.conversation_history: List[Dict[str, str]] = []
        
        self.system_prompt = """Ты — Джарвис, высокоинтеллектуальный AI-ассистент, созданный по образу Джарвиса из вселенной Marvel. 
Твои характеристики:
- Ты вежлив, профессионален и слегка саркастичен в британском стиле
- Обращаешься к пользователю "сэр" или "сэр/мадам"
- Даёшь краткие, но информативные ответы
- Ты можешь помочь с информацией, расчётами, советами
- Если не знаешь точного ответа, честно об этом говоришь
- Ты помнишь контекст разговора
- Отвечай на том же языке, на котором задан вопрос (русский или английский)

Будь полезным и эффективным помощником!"""
    
    async def get_response(self, user_message: str, use_history: bool = True) -> Optional[str]:
        try:
            messages = []
            
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
            
            if use_history and self.conversation_history:
                messages.extend(self.conversation_history[-10:])
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            logger.info(f"Sending request to GPT-4: {user_message}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            
            assistant_message = response.choices[0].message.content
            
            if use_history:
                self.conversation_history.append({
                    "role": "user",
                    "content": user_message
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
            
            logger.info(f"GPT-4 response: {assistant_message}")
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error getting GPT-4 response: {e}")
            return None
    
    def clear_history(self):
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, str]]:
        return self.conversation_history
