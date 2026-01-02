#!/bin/bash

echo "🤖 Запуск Jarvis AI Desktop Application"
echo "======================================"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Запустите сначала install-desktop.sh"
    exit 1
fi

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не найден. Запустите сначала install-desktop.sh"
    exit 1
fi

# Проверка зависимостей
if [ ! -d "node_modules" ]; then
    echo "📦 Устанавливаем зависимости..."
    npm install
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Устанавливаем frontend зависимости..."
    cd frontend && npm install && cd ..
fi

# Проверка переменных окружения
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден. Создаем из примера..."
    cp .env.example .env
    echo "📝 Отредактируйте файл .env и добавьте ваши API ключи"
fi

echo "🚀 Запуск десктопного приложения..."
npm run dev