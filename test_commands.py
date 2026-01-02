#!/usr/bin/env python3
"""
Скрипт для тестирования команд Jarvis AI через HTTP API
"""

import requests
import json
from datetime import datetime


API_URL = "http://localhost:8000"


def test_health():
    """Тест health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_command(command: str):
    """Тест обработки команды"""
    print(f"\n=== Testing Command: '{command}' ===")
    try:
        payload = {
            "command": command,
            "timestamp": datetime.now().isoformat()
        }
        response = requests.post(
            f"{API_URL}/api/command",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response']}")
            print(f"Command Type: {result['command_type']}")
            print(f"Has Audio: {'Yes' if result.get('audio_url') else 'No'}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("Jarvis AI - Test Suite")
    print("=" * 60)
    
    if not test_health():
        print("\n❌ Backend не доступен. Убедитесь что сервер запущен.")
        return
    
    print("\n✅ Backend работает корректно")
    
    test_commands = [
        "Привет Джарвис",
        "Какое время",
        "Включить свет",
        "Выключить свет",
        "Какая погода",
        "Напомни мне купить молоко",
        "Расскажи анекдот",
        "Сколько будет 2 плюс 2",
    ]
    
    print("\n" + "=" * 60)
    print("Testing Commands")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for command in test_commands:
        if test_command(command):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
