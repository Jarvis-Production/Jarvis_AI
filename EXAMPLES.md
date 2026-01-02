# Примеры использования Jarvis AI

## 📝 Примеры команд

### Предустановленные команды

#### Приветствие
```
Пользователь: "Привет Джарвис"
Джарвис: "Здравствуйте, сэр. Чем могу помочь?"
```

#### Время
```
Пользователь: "Какое время?"
Джарвис: "Сейчас 14:30"
```

#### Управление светом
```
Пользователь: "Включи свет"
Джарвис: "Свет включён, сэр."

Пользователь: "Выключи свет"
Джарвис: "Свет выключен, сэр."
```

#### Погода
```
Пользователь: "Какая погода?"
Джарвис: "Сейчас в Москве 5 градусов, облачно с прояснениями."
```

#### Напоминания
```
Пользователь: "Напомни мне купить молоко"
Джарвис: "Хорошо, я напомню вам о: купить молоко"
```

### GPT-4 команды

#### Общие вопросы
```
Пользователь: "Расскажи о космосе"
Джарвис: "Космос - это необъятное пространство за пределами Земли..."
```

#### Вычисления
```
Пользователь: "Сколько будет 15 процентов от 2000?"
Джарвис: "15% от 2000 составляет 300, сэр."
```

#### Советы
```
Пользователь: "Посоветуй хороший фильм про космос"
Джарвис: "Рекомендую 'Интерстеллар' режиссёра Кристофера Нолана..."
```

#### Рецепты
```
Пользователь: "Как приготовить омлет?"
Джарвис: "Для приготовления омлета вам понадобится..."
```

## 🔧 Примеры API

### HTTP API

#### Проверка здоровья
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-02T14:30:00",
  "api_keys_configured": true,
  "missing_keys": []
}
```

#### Отправка команды
```bash
curl -X POST "http://localhost:8000/api/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "Привет Джарвис",
    "timestamp": "2024-01-02T14:30:00"
  }'
```

Response:
```json
{
  "response": "Здравствуйте, сэр. Чем могу помочь?",
  "audio_url": "data:audio/mpeg;base64,...",
  "command_type": "predefined",
  "timestamp": "2024-01-02T14:30:00"
}
```

### WebSocket API

#### Подключение
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/client_123');

ws.onopen = () => {
  console.log('Connected to Jarvis');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

#### Отправка текстовой команды
```javascript
ws.send(JSON.stringify({
  type: 'text',
  data: {
    text: 'Привет Джарвис'
  }
}));
```

#### Отправка аудио данных
```javascript
const audioBlob = await mediaRecorder.stop();
const arrayBuffer = await audioBlob.arrayBuffer();
ws.send(arrayBuffer);
```

#### Получение ответов
```javascript
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'transcription':
      console.log('You said:', message.data.text);
      break;
    
    case 'response':
      console.log('Jarvis:', message.data.text);
      if (message.data.audio) {
        playAudio(message.data.audio);
      }
      break;
    
    case 'volume':
      console.log('Volume:', message.data.volume);
      break;
    
    case 'status':
      console.log('Status:', message.data.message);
      break;
  }
};
```

## 🎨 Примеры интеграции

### React Component
```tsx
import { useState, useEffect } from 'react';
import { WebSocketClient } from './utils/websocketClient';

function MyJarvisComponent() {
  const [response, setResponse] = useState('');
  const [wsClient, setWsClient] = useState<WebSocketClient | null>(null);

  useEffect(() => {
    const client = new WebSocketClient('ws://localhost:8000', 'my-client');
    
    client.connect({
      onResponse: (text, audio) => {
        setResponse(text);
        if (audio) {
          new Audio(audio).play();
        }
      }
    });

    setWsClient(client);

    return () => client.disconnect();
  }, []);

  const sendCommand = (command: string) => {
    wsClient?.sendText(command);
  };

  return (
    <div>
      <button onClick={() => sendCommand('Привет Джарвис')}>
        Say Hello
      </button>
      <p>{response}</p>
    </div>
  );
}
```

### Python Script
```python
import asyncio
import websockets
import json

async def talk_to_jarvis():
    uri = "ws://localhost:8000/ws/python_client"
    
    async with websockets.connect(uri) as websocket:
        message = {
            "type": "text",
            "data": {"text": "Привет Джарвис"}
        }
        
        await websocket.send(json.dumps(message))
        
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            
            if data['type'] == 'response':
                print(f"Jarvis: {data['data']['text']}")
                break

asyncio.run(talk_to_jarvis())
```

## 🎯 Сценарии использования

### Умный дом
```
"Включи свет в гостиной"
"Установи температуру 22 градуса"
"Закрой шторы"
```

### Продуктивность
```
"Напомни мне о встрече в 15:00"
"Какие у меня планы на сегодня?"
"Установи таймер на 25 минут"
```

### Информация
```
"Какая погода на завтра?"
"Какой курс доллара?"
"Последние новости"
```

### Развлечения
```
"Расскажи анекдот"
"Включи музыку"
"Посоветуй фильм"
```

## 🚀 Расширенные примеры

### Создание собственной команды

```python
# backend/services/command_processor.py

async def custom_command(self, text: str) -> str:
    # Ваша логика
    result = perform_some_action()
    return f"Выполнено: {result}"

# Добавьте в __init__
self.predefined_commands["моя команда"] = self.custom_command
```

### Интеграция с внешним API

```python
async def check_stocks(self, text: str) -> str:
    symbol = extract_symbol(text)  # Например, "AAPL"
    
    async with aiohttp.ClientSession() as session:
        url = f"https://api.example.com/stocks/{symbol}"
        async with session.get(url) as response:
            data = await response.json()
            price = data['price']
            return f"Цена {symbol}: ${price}"
```

### Кастомный голос

```python
# backend/config.py
ELEVENLABS_VOICE_ID = "your_custom_voice_id"

# Получить список доступных голосов
voices = await text_to_speech.get_available_voices()
for voice in voices:
    print(f"{voice['name']}: {voice['voice_id']}")
```

## 📚 Дополнительные ресурсы

- [OpenAI API Docs](https://platform.openai.com/docs)
- [ElevenLabs API Docs](https://elevenlabs.io/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)

---

Больше примеров на [GitHub Wiki](https://github.com/yourusername/Jarvis_AI/wiki)
