# 📁 Структура проекта Jarvis AI

## 🏗️ Общая структура

```
Jarvis_AI/
├── 📂 backend/                 # Backend приложение (Python/FastAPI)
├── 📂 frontend/                # Frontend приложение (React/TypeScript)
├── 📄 requirements.txt         # Python зависимости
├── 📄 .env.example             # Пример конфигурации
├── 📄 .gitignore               # Git ignore правила
├── 📄 docker-compose.yml       # Docker Compose конфигурация
├── 📄 Dockerfile.backend       # Dockerfile для backend
├── 📄 start.sh                 # Скрипт запуска (Linux/macOS)
├── 📄 start.bat                # Скрипт запуска (Windows)
├── 📄 test_commands.py         # Тестовый скрипт
├── 📄 README.md                # Основная документация
├── 📄 QUICK_START.md           # Быстрый старт
├── 📄 EXAMPLES.md              # Примеры использования
├── 📄 CONTRIBUTING.md          # Руководство для контрибьюторов
└── 📄 LICENSE                  # Лицензия MIT
```

## 🐍 Backend структура

```
backend/
├── 📄 __init__.py              # Пакет backend
├── 📄 main.py                  # Главное FastAPI приложение
│   ├── FastAPI app инициализация
│   ├── CORS middleware
│   ├── WebSocket endpoint (/ws/{client_id})
│   ├── HTTP endpoints (/, /health, /api/command)
│   └── Connection manager для WebSocket
│
├── 📄 config.py                # Конфигурация приложения
│   ├── Settings класс
│   ├── Загрузка .env переменных
│   ├── API ключи (OpenAI, ElevenLabs, OpenWeatherMap)
│   └── Валидация конфигурации
│
├── 📄 models.py                # Pydantic модели данных
│   ├── AudioData - модель аудио данных
│   ├── TranscriptionResponse - результат распознавания
│   ├── CommandRequest - запрос команды
│   ├── CommandResponse - ответ на команду
│   ├── WebSocketMessage - WebSocket сообщение
│   └── AssistantState - состояние ассистента
│
└── 📂 services/                # Сервисный слой
    ├── 📄 __init__.py          # Экспорт сервисов
    │
    ├── 📄 audio_processing.py  # Обработка аудио
    │   ├── AudioProcessor класс
    │   ├── calculate_volume() - расчёт громкости
    │   ├── decode_base64_audio() - декодирование base64
    │   ├── convert_to_wav() - конвертация в WAV
    │   ├── normalize_audio() - нормализация аудио
    │   └── detect_speech() - детекция речи
    │
    ├── 📄 speech_recognition.py # Распознавание речи (Whisper)
    │   ├── SpeechRecognizer класс
    │   ├── transcribe_audio() - распознавание аудио
    │   └── transcribe_audio_detailed() - детальное распознавание
    │
    ├── 📄 command_processor.py  # Обработка команд
    │   ├── CommandProcessor класс
    │   ├── process_command() - основная обработка
    │   ├── Предустановленные команды:
    │   │   ├── greeting_command() - приветствие
    │   │   ├── time_command() - текущее время
    │   │   ├── light_on_command() - включение света
    │   │   ├── light_off_command() - выключение света
    │   │   ├── weather_command() - погода
    │   │   ├── reminder_command() - напоминания
    │   │   └── shutdown_command() - выключение
    │   └── get_reminders() - получение напоминаний
    │
    ├── 📄 llm_handler.py        # GPT-4 интеграция
    │   ├── LLMHandler класс
    │   ├── get_response() - получение ответа от GPT-4
    │   ├── Система промпт для Джарвиса
    │   ├── История разговоров
    │   ├── clear_history() - очистка истории
    │   └── get_history() - получение истории
    │
    └── 📄 text_to_speech.py     # Синтез речи (ElevenLabs)
        ├── TextToSpeech класс
        ├── synthesize_speech() - синтез речи
        ├── synthesize_speech_base64() - синтез в base64
        └── get_available_voices() - доступные голоса
```

## ⚛️ Frontend структура

```
frontend/
├── 📄 package.json             # Node.js зависимости и скрипты
├── 📄 tsconfig.json            # TypeScript конфигурация
├── 📄 tsconfig.node.json       # TypeScript для Node.js
├── 📄 vite.config.ts           # Vite конфигурация
├── 📄 index.html               # HTML точка входа
├── 📄 .env.example             # Пример переменных окружения
├── 📄 Dockerfile               # Dockerfile для frontend
│
└── 📂 src/                     # Исходный код
    ├── 📄 main.tsx             # Точка входа React
    ├── 📄 App.tsx              # Главный App компонент
    ├── 📄 vite-env.d.ts        # TypeScript определения для Vite
    │
    ├── 📂 components/          # React компоненты
    │   ├── 📄 JarvisAssistant.tsx  # Главный компонент ассистента
    │   │   ├── WebSocket подключение
    │   │   ├── Управление микрофоном
    │   │   ├── Обработка аудио
    │   │   ├── Отображение статуса
    │   │   └── Управление состоянием
    │   │
    │   ├── 📄 WaveAnimation.tsx    # Анимация волн
    │   │   ├── Canvas анимация
    │   │   ├── Пульсирующие волны
    │   │   └── Зависимость от громкости
    │   │
    │   └── 📄 CommandHistory.tsx   # История команд
    │       ├── Список команд
    │       ├── История взаимодействий
    │       └── Кнопка очистки
    │
    ├── 📂 utils/               # Утилиты
    │   ├── 📄 websocketClient.ts   # WebSocket клиент
    │   │   ├── WebSocketClient класс
    │   │   ├── connect() - подключение
    │   │   ├── sendText() - отправка текста
    │   │   ├── sendAudio() - отправка аудио
    │   │   ├── sendControl() - управляющие команды
    │   │   └── Автоматическое переподключение
    │   │
    │   └── 📄 audioProcessor.ts    # Обработка аудио
    │       ├── AudioProcessorUtil класс
    │       ├── initialize() - инициализация микрофона
    │       ├── getVolume() - получение громкости
    │       ├── startRecording() - запуск записи
    │       ├── stopRecording() - остановка записи
    │       ├── cleanup() - очистка ресурсов
    │       └── playAudioFromBase64() - воспроизведение аудио
    │
    └── 📂 styles/              # Стили
        └── 📄 main.css         # Основные стили
            ├── Cyberpunk тема
            ├── Анимации
            ├── Градиенты
            ├── Эффекты свечения
            └── Адаптивный дизайн
```

## 🔄 Поток данных

### Распознавание речи

```
1. Пользователь → Нажатие кнопки микрофона
2. Frontend → Запуск записи аудио (MediaRecorder)
3. Frontend → Вычисление громкости в реальном времени
4. Frontend → Остановка записи через 5 секунд
5. Frontend → Отправка аудио через WebSocket
6. Backend → Получение аудио данных
7. Backend → Конвертация в WAV формат
8. Backend → Отправка в OpenAI Whisper API
9. Backend → Получение транскрипции
10. Backend → Отправка транскрипции на frontend
11. Frontend → Отображение текста пользователя
```

### Обработка команды

```
1. Backend → Получение транскрипции
2. Backend → Проверка предустановленных команд
3a. Если найдена → Выполнение предустановленной команды
3b. Если не найдена → Отправка в GPT-4
4. Backend → Получение текста ответа
5. Backend → Отправка в ElevenLabs для синтеза речи
6. Backend → Получение аудио (MP3)
7. Backend → Конвертация в base64
8. Backend → Отправка текста и аудио на frontend
9. Frontend → Отображение текста ответа
10. Frontend → Воспроизведение аудио ответа
```

### WebSocket сообщения

```
Frontend → Backend:
- type: "audio" - аудио данные (binary)
- type: "text" - текстовая команда
- type: "control" - управляющие команды

Backend → Frontend:
- type: "transcription" - результат распознавания
- type: "response" - ответ ассистента (текст + аудио)
- type: "status" - статус обработки
- type: "volume" - уровень громкости
- type: "error" - ошибка
- type: "reminders" - список напоминаний
```

## 🎯 Основные классы и их назначение

### Backend

| Класс | Файл | Назначение |
|-------|------|-----------|
| `Settings` | config.py | Конфигурация приложения |
| `AudioProcessor` | audio_processing.py | Обработка аудио данных |
| `SpeechRecognizer` | speech_recognition.py | Распознавание речи через Whisper |
| `CommandProcessor` | command_processor.py | Обработка и выполнение команд |
| `LLMHandler` | llm_handler.py | Интеграция с GPT-4 |
| `TextToSpeech` | text_to_speech.py | Синтез речи через ElevenLabs |
| `ConnectionManager` | main.py | Управление WebSocket соединениями |

### Frontend

| Компонент/Класс | Файл | Назначение |
|----------------|------|-----------|
| `JarvisAssistant` | JarvisAssistant.tsx | Главный UI компонент |
| `WaveAnimation` | WaveAnimation.tsx | Canvas анимация волн |
| `CommandHistory` | CommandHistory.tsx | История команд |
| `WebSocketClient` | websocketClient.ts | WebSocket клиент |
| `AudioProcessorUtil` | audioProcessor.ts | Обработка аудио в браузере |

## 🔧 Технологии

### Backend
- **FastAPI** - Web framework
- **WebSockets** - Real-time коммуникация
- **OpenAI SDK** - Whisper и GPT-4
- **aiohttp** - Async HTTP клиент
- **numpy** - Обработка аудио массивов
- **pydantic** - Валидация данных

### Frontend
- **React 18** - UI библиотека
- **TypeScript** - Типизация
- **Vite** - Сборщик и dev сервер
- **Web Audio API** - Работа с аудио
- **WebSocket API** - Real-time соединение
- **Canvas API** - Анимация волн

## 📦 Зависимости

### Python (requirements.txt)
```
fastapi==0.108.0           # Web framework
uvicorn[standard]==0.25.0  # ASGI server
websockets==12.0           # WebSocket support
python-dotenv==1.0.0       # Environment variables
openai==1.6.1              # OpenAI API client
aiohttp==3.9.1             # Async HTTP client
numpy==1.26.2              # Array processing
pydantic==2.5.3            # Data validation
python-multipart==0.0.6    # Multipart form support
```

### Node.js (package.json)
```
react@18.2.0               # UI library
react-dom@18.2.0           # React DOM
typescript@5.3.3           # TypeScript
vite@5.0.8                 # Build tool
@vitejs/plugin-react@4.2.1 # Vite React plugin
```

## 🚀 Deployment

### Docker
- `Dockerfile.backend` - Multi-stage build для backend
- `frontend/Dockerfile` - Node.js build для frontend
- `docker-compose.yml` - Оркестрация обоих сервисов

### Переменные окружения
- `.env` (root) - Backend конфигурация
- `frontend/.env` - Frontend конфигурация (только VITE_ переменные)

---

Для более детальной информации см. [README.md](README.md)
