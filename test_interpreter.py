"""
Тестовый скрипт для проверки интерпретатора УВМ.
"""

import os
import subprocess
import sys

def test_interpreter():
    """Запускает тесты интерпретатора."""
    print("🧪 Тестирование интерпретатора УВМ (Этап 3)")
    print("="*60)
    
    # Шаг 1: Ассемблируем тестовую программу
    print("\n1. Ассемблирование тестовой программы...")
    result = subprocess.run(
        [sys.executable, "assembler.py", "test_program.yaml", "test_output.bin"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Ошибка ассемблирования: {result.stderr}")
        return False
    
    print("✅ Ассемблирование успешно")
    
    # Шаг 2: Запуск интерпретатора
    print("\n2. Запуск интерпретатора...")
    result = subprocess.run(
        [sys.executable, "interpreter.py", "test_output.bin", "--dump-memory"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Ошибка интерпретатора: {result.stderr}")
        return False
    
    print("✅ Интерпретатор успешно выполнил программу")
    
    # Шаг 3: Проверка существования дампа памяти
    print("\n3. Проверка дампа памяти...")
    if os.path.exists("memory_dump.xml"):
        print("✅ XML дамп памяти создан")
        
        # Читаем и выводим часть дампа
        with open("memory_dump.xml", "r") as f:
            content = f.read(500)
            print(f"   Начало XML:\n{content}...")
    else:
        print("❌ XML дамп не создан")
        return False
    
    # Шаг 4: Очистка временных файлов
    print("\n4. Очистка временных файлов...")
    for file in ["test_output.bin", "memory_dump.xml"]:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Удален: {file}")
    
    print("\n" + "="*60)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    if test_interpreter():
        sys.exit(0)
    else:
        sys.exit(1)
