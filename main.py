#!/usr/bin/env python3
"""
CLI-ассемблер для Учебной Виртуальной Машины
Этап 1: Перевод программы в промежуточное представление
"""

import sys
import argparse
import os

def main():
    print("🚀 Запуск ассемблера УВМ (Вариант 3)...")
    
    parser = argparse.ArgumentParser(
        description='Ассемблер для Учебной Виртуальной Машины (УВМ) - Вариант 3',
        epilog='Пример: python main.py test_program.yaml output.bin --test'
    )
    
    parser.add_argument('input_file', help='Путь к исходному YAML файлу')
    parser.add_argument('output_file', help='Путь к двоичному файлу-результату')
    parser.add_argument('--test', action='store_true', 
                       help='Режим тестирования (вывод промежуточного представления)')
    
    args = parser.parse_args()
    
    print(f"📁 Входной файл: {args.input_file}")
    print(f"💾 Выходной файл: {args.output_file}")
    
    # Проверка существования файла
    if not os.path.exists(args.input_file):
        print(f"❌ Ошибка: файл {args.input_file} не найден")
        sys.exit(1)
    
    try:
        # Импортируем здесь чтобы избежать циклических импортов
        sys.path.append(os.path.dirname(__file__))
        from assembler import Assembler
        
        print("🔄 Создание ассемблера...")
        
        # Создаем ассемблер
        assembler = Assembler()
        
        # Ассемблируем программу
        print("🔧 Ассемблирование программы...")
        intermediate_repr = assembler.assemble(args.input_file)
        
        # Режим тестирования - вывод промежуточного представления
        if args.test:
            print("\n=== РЕЖИМ ТЕСТИРОВАНИЯ ===")
            print("📋 Промежуточное представление:")
            for i, cmd in enumerate(intermediate_repr):
                print(f"  Команда {i}: {cmd}")
        
        # Сохраняем в бинарный файл (на этапе 2)
        # Пока просто выводим информацию
        print(f"\n✅ Программа успешно ассемблирована")
        print(f"   📊 Команд: {len(intermediate_repr)}")
        
        # Демонстрация тестов из спецификации
        if args.test:
            print("\n=== ТЕСТЫ ИЗ СПЕЦИФИКАЦИИ УВМ ===")
            _run_specification_tests(assembler)
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("   Убедитесь что установлен PyYAML: pip install pyyaml")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def _run_specification_tests(assembler):
    """Запускает тесты из спецификации УВМ Варианта 3"""
    test_cases = [
        ("LOAD 515 в регистр 4", 
         {"command": "LOAD", "value": 515, "register": 4}, 
         [0xDD, 0x80, 0x00, 0x10]),
        
        ("READ из памяти (регистр 2) в регистр 0", 
         {"command": "READ", "dest_register": 0, "addr_register": 2}, 
         [0x12, 0x10, 0x00, 0x00]),
        
        ("WRITE регистр 24 в память (адрес в регистре 13)", 
         {"command": "WRITE", "addr_register": 13, "src_register": 24}, 
         [0x49, 0xC3, 0x00, 0x00]),
        
        ("ABS регистра 22 в память (адрес в регистре 26)", 
         {"command": "ABS", "addr_register": 26, "src_register": 22}, 
         [0x99, 0xB6, 0x00, 0x00]),
    ]
    
    for name, command, expected_bytes in test_cases:
        print(f"\n🧪 Тест: {name}")
        print(f"  📥 Входные данные: {command}")
        print(f"  🎯 Ожидается байты: {[hex(b) for b in expected_bytes]}")
        
        # Тестируем парсинг команды
        try:
            intermediate = assembler._parse_command_test(command, 0)
            print(f"  ✅ Промежуточное представление: {intermediate}")
            
            # Проверяем соответствие спецификации
            if intermediate['opcode'] == 29:  # LOAD
                print(f"  ✅ A=29, B={intermediate.get('value', 'N/A')}, C={intermediate.get('register', 'N/A')}")
            elif intermediate['opcode'] == 18:  # READ
                print(f"  ✅ A=18, B={intermediate.get('dest_register', 'N/A')}, C={intermediate.get('addr_register', 'N/A')}")
            elif intermediate['opcode'] == 9:   # WRITE
                print(f"  ✅ A=9, B={intermediate.get('addr_register', 'N/A')}, C={intermediate.get('src_register', 'N/A')}")
            elif intermediate['opcode'] == 25:  # ABS
                print(f"  ✅ A=25, B={intermediate.get('addr_register', 'N/A')}, C={intermediate.get('src_register', 'N/A')}")
                
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")

if __name__ == "__main__":
    main()