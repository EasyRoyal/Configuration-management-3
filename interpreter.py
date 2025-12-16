"""
Этап 3: Интерпретатор и операции с памятью
"""

import argparse
import struct
import sys
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from spec import UVMSpec

class UVMMemory:
    """Модель памяти УВМ с разделением памяти команд и данных."""
    
    def __init__(self, data_size=1024, reg_count=32):
        """
        Инициализация памяти УВМ.
        
        Args:
            data_size: Размер памяти данных (в словах)
            reg_count: Количество регистров
        """
        # Память команд (хранит бинарный код программы)
        self.code_memory = bytearray()
        
        # Память данных (32-битные слова)
        self.data_memory = [0] * data_size
        
        # Регистры (32-битные)
        self.registers = [0] * reg_count
        
        # Счетчик команд
        self.pc = 0
        
        # Флаг завершения программы
        self.halted = False
        
        # Статистика выполнения
        self.stats = {
            'instructions_executed': 0,
            'memory_reads': 0,
            'memory_writes': 0
        }
    
    def load_program(self, binary_path):
        """
        Загружает бинарную программу в память команд.
        
        Args:
            binary_path: Путь к бинарному файлу
            
        Raises:
            FileNotFoundError: Если файл не найден
        """
        try:
            with open(binary_path, 'rb') as f:
                self.code_memory = bytearray(f.read())
            
            print(f"✓ Программа загружена: {len(self.code_memory)} байт")
            
            # Проверяем размер программы (должен быть кратен 4 байтам)
            if len(self.code_memory) % 4 != 0:
                print(f"⚠ Предупреждение: размер программы не кратен 4 байтам")
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл программы не найден: {binary_path}")
    
    def read_instruction(self):
        """
        Читает следующую инструкцию из памяти команд.
        
        Returns:
            bytes: 4 байта инструкции или None если конец программы
            
        Raises:
            IndexError: Если вышли за пределы памяти
        """
        if self.pc >= len(self.code_memory):
            self.halted = True
            return None
        
        if self.pc + 4 > len(self.code_memory):
            # Читаем оставшиеся байты
            instruction = self.code_memory[self.pc:]
            self.pc = len(self.code_memory)
        else:
            instruction = self.code_memory[self.pc:self.pc + 4]
            self.pc += 4
        
        return instruction
    
    def decode_instruction(self, instruction_bytes):
        """
        Декодирует бинарную инструкцию в промежуточное представление.
        
        Args:
            instruction_bytes: 4 байта инструкции
            
        Returns:
            dict: Декодированная команда
            
        Raises:
            ValueError: Если инструкция некорректна
        """
        if len(instruction_bytes) != 4:
            raise ValueError(f"Инструкция должна быть 4 байта, получено {len(instruction_bytes)}")
        
        # Конвертируем в целое число (little-endian)
        instruction = int.from_bytes(instruction_bytes, byteorder='little')
        
        # Извлекаем опкод (биты 0-5)
        opcode = (instruction >> 0) & 0x3F
        
        # Определяем формат команды и извлекаем операнды
        if opcode == UVMSpec.LOAD_CONST:
            # Формат LOAD_CONST: A=опкод, B=константа (20 бит), C=адрес (5 бит)
            B = (instruction >> 6) & 0xFFFFF  # 20 бит
            C = (instruction >> 26) & 0x1F    # 5 бит
        else:
            # Формат остальных команд: A=опкод, B=адрес (5 бит), C=адрес (5 бит)
            B = (instruction >> 6) & 0x1F    # 5 бит
            C = (instruction >> 11) & 0x1F   # 5 бит
        
        # Создаем промежуточное представление
        decoded = {
            'opcode': opcode,
            'operands': {
                'B': B,
                'C': C
            },
            'description': UVMSpec.get_command_description(opcode, {'B': B, 'C': C}),
            'bytes': instruction_bytes
        }
        
        # Валидируем команду
        try:
            UVMSpec.validate_command(opcode, {'B': B, 'C': C})
        except ValueError as e:
            raise ValueError(f"Некорректная инструкция: {e}")
        
        return decoded
    
    def execute_load_const(self, operands):
        """
        Выполняет команду LOAD_CONST.
        
        Args:
            operands: Словарь с операндами {'B': константа, 'C': адрес_регистра}
        """
        const_value = operands['B']
        reg_addr = operands['C']
        
        # Загружаем константу в регистр
        self.registers[reg_addr] = const_value
        
        print(f"  R{reg_addr} = {const_value} (0x{const_value:X})")
    
    def execute_read_mem(self, operands):
        """
        Выполняет команду READ_MEM.
        
        Args:
            operands: Словарь с операндами {'B': адрес_регистра_назначения, 
                                           'C': адрес_регистра_источника}
        """
        dest_reg = operands['B']
        src_reg = operands['C']
        
        # Получаем адрес в памяти данных из регистра-источника
        mem_addr = self.registers[src_reg]
        
        # Проверяем границы памяти
        if 0 <= mem_addr < len(self.data_memory):
            # Читаем значение из памяти данных
            value = self.data_memory[mem_addr]
            
            # Записываем в регистр-назначение
            self.registers[dest_reg] = value
            
            self.stats['memory_reads'] += 1
            
            print(f"  R{dest_reg} = M[R{src_reg}={mem_addr}] = {value}")
        else:
            raise IndexError(f"Адрес памяти вне диапазона: {mem_addr}")
    
    def execute_write_mem(self, operands):
        """
        Выполняет команду WRITE_MEM.
        
        Args:
            operands: Словарь с операндами {'B': адрес_регистра_памяти, 
                                           'C': адрес_регистра_источника}
        """
        mem_reg = operands['B']
        src_reg = operands['C']
        
        # Получаем адрес в памяти данных из регистра памяти
        mem_addr = self.registers[mem_reg]
        
        # Получаем значение из регистра-источника
        value = self.registers[src_reg]
        
        # Проверяем границы памяти
        if 0 <= mem_addr < len(self.data_memory):
            # Записываем значение в память данных
            self.data_memory[mem_addr] = value
            
            self.stats['memory_writes'] += 1
            
            print(f"  M[R{mem_reg}={mem_addr}] = R{src_reg} = {value}")
        else:
            raise IndexError(f"Адрес памяти вне диапазона: {mem_addr}")
    
    def execute_instruction(self, decoded):
        """
        Выполняет декодированную инструкцию.
        
        Args:
            decoded: Декодированная команда
            
        Raises:
            ValueError: Если опкод неизвестен
        """
        opcode = decoded['opcode']
        operands = decoded['operands']
        
        print(f"  Выполнение: {decoded['description']}")
        
        if opcode == UVMSpec.LOAD_CONST:
            self.execute_load_const(operands)
        elif opcode == UVMSpec.READ_MEM:
            self.execute_read_mem(operands)
        elif opcode == UVMSpec.WRITE_MEM:
            self.execute_write_mem(operands)
        elif opcode == UVMSpec.ABS:
            # ABS будет реализован в этапе 4
            print(f"  ⚠ Команда ABS пока не реализована (этап 4)")
            # Временно выполняем как NOP
            pass
        else:
            raise ValueError(f"Неизвестный опкод: {opcode}")
    
    def step(self):
        """
        Выполняет один шаг программы.
        
        Returns:
            bool: True если инструкция выполнена, False если программа завершена
        """
        if self.halted:
            return False
        
        # Читаем инструкцию
        instruction_bytes = self.read_instruction()
        
        if instruction_bytes is None:
            self.halted = True
            return False
        
        # Декодируем инструкцию
        try:
            decoded = self.decode_instruction(instruction_bytes)
        except ValueError as e:
            print(f"❌ Ошибка декодирования: {e}")
            self.halted = True
            return False
        
        # Выполняем инструкцию
        try:
            self.execute_instruction(decoded)
            self.stats['instructions_executed'] += 1
        except (ValueError, IndexError) as e:
            print(f"❌ Ошибка выполнения: {e}")
            self.halted = True
            return False
        
        return True
    
    def run(self, max_steps=1000):
        """
        Запускает выполнение программы.
        
        Args:
            max_steps: Максимальное количество инструкций для выполнения
            
        Returns:
            bool: True если программа завершилась успешно
        """
        print(f"\n{'='*60}")
        print("ЗАПУСК ИНТЕРПРЕТАТОРА УВМ")
        print(f"{'='*60}")
        
        step_count = 0
        while not self.halted and step_count < max_steps:
            print(f"\nШаг {step_count + 1} (PC={self.pc}):")
            
            if not self.step():
                break
            
            step_count += 1
        
        if self.halted:
            print(f"\n✓ Программа завершена")
        elif step_count >= max_steps:
            print(f"\n⚠ Достигнут лимит выполнения ({max_steps} инструкций)")
        
        return self.halted
    
    def dump_memory_xml(self, start_addr=0, end_addr=None, output_path="memory_dump.xml"):
        """
        Сохраняет дамп памяти в XML формате.
        
        Args:
            start_addr: Начальный адрес для дампа
            end_addr: Конечный адрес для дампа (None = до конца памяти)
            output_path: Путь для сохранения XML файла
            
        Returns:
            str: Строка XML дампа
        """
        if end_addr is None:
            end_addr = min(len(self.data_memory), start_addr + 100)  # Ограничиваем дамп
        
        # Создаем корневой элемент
        root = ET.Element("uvm_memory_dump")
        
        # Добавляем информацию о программе
        info = ET.SubElement(root, "program_info")
        ET.SubElement(info, "instructions_executed").text = str(self.stats['instructions_executed'])
        ET.SubElement(info, "memory_reads").text = str(self.stats['memory_reads'])
        ET.SubElement(info, "memory_writes").text = str(self.stats['memory_writes'])
        ET.SubElement(info, "program_counter").text = str(self.pc)
        
        # Добавляем регистры
        registers_elem = ET.SubElement(root, "registers")
        for i, value in enumerate(self.registers):
            if value != 0:  # Сохраняем только ненулевые регистры
                reg_elem = ET.SubElement(registers_elem, "register")
                reg_elem.set("id", str(i))
                reg_elem.set("value", str(value))
                reg_elem.set("hex", f"0x{value:X}")
        
        # Добавляем память данных
        memory_elem = ET.SubElement(root, "data_memory")
        memory_elem.set("start_address", str(start_addr))
        memory_elem.set("end_address", str(end_addr))
        memory_elem.set("total_size", str(len(self.data_memory)))
        
        for addr in range(start_addr, min(end_addr, len(self.data_memory))):
            value = self.data_memory[addr]
            if value != 0:  # Сохраняем только ненулевые ячейки
                cell_elem = ET.SubElement(memory_elem, "memory_cell")
                cell_elem.set("address", str(addr))
                cell_elem.set("value", str(value))
                cell_elem.set("hex", f"0x{value:X}")
        
        # Форматируем XML
        xml_str = ET.tostring(root, encoding='unicode')
        
        # Используем minidom для красивого форматирования
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        # Сохраняем в файл
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"✓ Дамп памяти сохранен в: {output_path}")
        
        return pretty_xml
    
    def print_status(self):
        """Выводит текущее состояние памяти и регистров."""
        print(f"\n{'='*60}")
        print("СОСТОЯНИЕ УВМ:")
        print(f"{'='*60}")
        
        # Регистры
        print("\n📊 Регистры (ненулевые):")
        for i, value in enumerate(self.registers):
            if value != 0:
                print(f"  R{i:2d} = {value:10d} (0x{value:08X})")
        
        # Память данных (первые 16 ячеек)
        print("\n💾 Память данных (первые 16 ячеек):")
        for i in range(0, min(16, len(self.data_memory))):
            value = self.data_memory[i]
            if value != 0:
                print(f"  M[{i:3d}] = {value:10d} (0x{value:08X})")
        
        # Статистика
        print(f"\n📈 Статистика выполнения:")
        print(f"  • Выполнено инструкций: {self.stats['instructions_executed']}")
        print(f"  • Чтений из памяти: {self.stats['memory_reads']}")
        print(f"  • Записей в память: {self.stats['memory_writes']}")
        print(f"  • Счетчик команд (PC): {self.pc}")
        print(f"{'='*60}")


class InterpreterCLI:
    """CLI интерфейс для интерпретатора УВМ."""
    
    def __init__(self):
        self.memory = UVMMemory()
    
    def run(self, args):
        """
        Запускает интерпретатор с заданными аргументами.
        
        Args:
            args: Аргументы командной строки
        """
        print(f"{'='*60}")
        print("ИНТЕРПРЕТАТОР УЧЕБНОЙ ВИРТУАЛЬНОЙ МАШИНЫ (УВМ)")
        print("Вариант №3 | РТУ МИРЭА | Этап 3: Интерпретатор и операции с памятью")
        print(f"{'='*60}")
        
        try:
            # Загружаем программу
            self.memory.load_program(args.binary_file)
            
            # Запускаем выполнение
            self.memory.run(max_steps=args.max_steps)
            
            # Выводим состояние
            self.memory.print_status()
            
            # Сохраняем дамп памяти
            if args.dump_memory:
                xml_dump = self.memory.dump_memory_xml(
                    start_addr=args.dump_start,
                    end_addr=args.dump_end,
                    output_path=args.dump_output
                )
                
                if args.verbose:
                    print("\n📋 Содержимое XML дампа:")
                    print(xml_dump[:500] + "..." if len(xml_dump) > 500 else xml_dump)
            
            print(f"\n✅ ВЫПОЛНЕНИЕ ПРОГРАММЫ ЗАВЕРШЕНО")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Точка входа в интерпретатор."""
    parser = argparse.ArgumentParser(
        description='Интерпретатор для учебной виртуальной машины (УВМ) - Вариант №3\n'
                    'Этап 3: Интерпретатор и операции с памятью',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Примеры использования:\n'
               '  python interpreter.py program.bin\n'
               '  python interpreter.py program.bin --dump-memory\n'
               '  python interpreter.py program.bin --dump-memory --dump-start 0 --dump-end 32\n'
    )
    
    parser.add_argument(
        'binary_file',
        help='Путь к бинарному файлу с ассемблированной программой'
    )
    
    parser.add_argument(
        '--dump-memory',
        action='store_true',
        help='Сохранить дамп памяти после выполнения программы'
    )
    
    parser.add_argument(
        '--dump-output',
        default='memory_dump.xml',
        help='Путь к файлу для сохранения дампа памяти (по умолчанию: memory_dump.xml)'
    )
    
    parser.add_argument(
        '--dump-start',
        type=int,
        default=0,
        help='Начальный адрес для дампа памяти (по умолчанию: 0)'
    )
    
    parser.add_argument(
        '--dump-end',
        type=int,
        default=32,
        help='Конечный адрес для дампа памяти (по умолчанию: 32)'
    )
    
    parser.add_argument(
        '--max-steps',
        type=int,
        default=1000,
        help='Максимальное количество инструкций для выполнения (по умолчанию: 1000)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Подробный вывод'
    )
    
    args = parser.parse_args()
    
    # Проверяем существование файла
    if not os.path.exists(args.binary_file):
        print(f"❌ Ошибка: файл программы '{args.binary_file}' не найден")
        sys.exit(1)
    
    # Запускаем интерпретатор
    interpreter = InterpreterCLI()
    interpreter.run(args)


if __name__ == "__main__":
    main()