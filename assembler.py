"""
Главный файл ассемблера для учебной виртуальной машины (УВМ).
Интегрирует Этапы 1 и 2.
"""

import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import YamlParser
from encoder import CommandEncoder
from spec import UVMSpec

class UVMAssembler:
    """Главный класс ассемблера УВМ."""
    
    def __init__(self):
        self.parser = YamlParser()
        self.encoder = CommandEncoder()
        self.intermediate = []
        self.binary_data = bytearray()
    
    def assemble(self, input_yaml, output_bin, test_mode=False):
        """
        Выполняет полный процесс ассемблирования.
        
        Args:
            input_yaml: Путь к входному YAML файлу
            output_bin: Путь к выходному бинарному файлу
            test_mode: Режим тестирования
            
        Returns:
            bool: True если успешно, False в противном случае
        """
        try:
            # Этап 1: Парсинг YAML
            print(f"\n{'='*60}")
            print("ЭТАП 1: ПАРСИНГ YAML ФАЙЛА")
            print(f"{'='*60}")
            print(f"Входной файл: {input_yaml}")
            
            self.intermediate = self.parser.parse(input_yaml)
            
            if test_mode:
                self.parser.print_intermediate(self.intermediate)
            
            # Этап 2: Кодирование в машинный код
            print(f"\n{'='*60}")
            print("ЭТАП 2: КОДИРОВАНИЕ В МАШИННЫЙ КОД")
            print(f"{'='*60}")
            print(f"Выходной файл: {output_bin}")
            
            self.binary_data = self.encoder.encode_program(self.intermediate)
            self.encoder.save_to_file(output_bin)
            
            if test_mode:
                self.encoder.print_encoded_commands()
            
            # Вывод статистики
            self._print_statistics(output_bin)
            
            return True
            
        except Exception as e:
            print(f"\n✗ ОШИБКА: {e}")
            return False
    
    def _print_statistics(self, output_path):
        """Выводит статистику ассемблирования."""
        stats = self.encoder.get_statistics(output_path)
        
        print(f"\n{'='*60}")
        print("СТАТИСТИКА АССЕМБЛИРОВАНИЯ:")
        print(f"{'='*60}")
        print(f"• Количество команд: {stats['command_count']}")
        print(f"• Общий размер данных: {stats['total_bytes']} байт")
        print(f"• Размер выходного файла: {stats['file_size']} байт")
        print(f"• Выходной файл: {stats['output_file']}")
        print(f"{'='*60}")
        
        # Проверяем тестовые команды
        if stats['command_count'] == 4:
            print("\n✓ Тестовая программа содержит все 4 команды из спецификации")
            print("  Ожидаемые результаты:")
            print("  1. LOAD_CONST: 0xDD, 0x80, 0x00, 0x10")
            print("  2. READ_MEM:   0x12, 0x10, 0x00, 0x00")
            print("  3. WRITE_MEM:  0x49, 0xC3, 0x00, 0x00")
            print("  4. ABS:        0x99, 0xB6, 0x00, 0x00")

def main():
    """Точка входа в программу."""
    parser = argparse.ArgumentParser(
        description='Ассемблер для учебной виртуальной машины (УВМ) - Вариант №3\n'
                    'Этапы 1-2: Парсинг YAML и генерация машинного кода',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Примеры использования:\n'
               '  python assembler.py program.yaml output.bin\n'
               '  python assembler.py test_program.asm.yaml test.bin --test'
    )
    
    parser.add_argument(
        'input_file',
        help='Путь к YAML файлу с программой на ассемблере УВМ'
    )
    
    parser.add_argument(
        'output_file',
        help='Путь для сохранения бинарного файла с машинным кодом'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Режим тестирования с подробным выводом промежуточных данных'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Ассемблер УВМ v1.0 (Вариант №3)'
    )
    
    args = parser.parse_args()
    
    # Проверяем существование входного файла
    if not os.path.exists(args.input_file):
        print(f"✗ Ошибка: Входной файл '{args.input_file}' не найден")
        sys.exit(1)
    
    # Создаем и запускаем ассемблер
    print(f"{'='*60}")
    print("АССЕМБЛЕР УЧЕБНОЙ ВИРТУАЛЬНОЙ МАШИНЫ (УВМ)")
    print("Вариант №3 | РТУ МИРЭА | Конфигурационное управление")
    print(f"{'='*60}")
    
    assembler = UVMAssembler()
    
    if args.test:
        print("⚡ РЕЖИМ ТЕСТИРОВАНИЯ: ВКЛЮЧЕН")
    
    success = assembler.assemble(args.input_file, args.output_file, args.test)
    
    if success:
        print(f"\n✅ АССЕМБЛИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print(f"{'='*60}")
    else:
        print(f"\n❌ АССЕМБЛИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ")
        sys.exit(1)

if __name__ == "__main__":
    main()