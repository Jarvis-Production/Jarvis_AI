#!/bin/bash

echo "🚀 Установка Jarvis AI Desktop Application"
echo "=========================================="

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8+ и попробуйте снова."
    exit 1
fi

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не найден. Установите Node.js 16+ и попробуйте снова."
    exit 1
fi

echo "✅ Python и Node.js найдены"

# Установка Python зависимостей
echo ""
echo "📦 Установка Python зависимостей..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Ошибка установки Python зависимостей"
    exit 1
fi

# Установка Node.js зависимостей
echo ""
echo "📦 Установка Node.js зависимостей..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Ошибка установки Node.js зависимостей"
    exit 1
fi

# Установка frontend зависимостей
echo ""
echo "📦 Установка frontend зависимостей..."
cd frontend && npm install && cd ..

if [ $? -ne 0 ]; then
    echo "❌ Ошибка установки frontend зависимостей"
    exit 1
fi

# Сборка frontend
echo ""
echo "🔨 Сборка frontend..."
cd frontend && npm run build && cd ..

if [ $? -ne 0 ]; then
    echo "❌ Ошибка сборки frontend"
    exit 1
fi

echo ""
echo "✅ Установка завершена успешно!"
echo ""
echo "🚀 Для запуска десктопного приложения выполните:"
echo "   npm run dev"
echo ""
echo "📱 Для сборки исполняемого файла:"
echo "   npm run dist"