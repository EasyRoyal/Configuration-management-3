#!/usr/bin/env python3
"""
encoder.py
Этап 2: Кодирование промежуточного представления в машинный код.
"""

import os
from spec import UVMSpec

class CommandEncoder:
    """Кодировщик команд УВМ в машинный код."""
    
    def __init__(self):
        self.binary_data = bytearray()
        self.encoded_commands = []
    
    def encode_command(self, cmd):
        """
        Кодирует одну команду в бинарное представление.
        
        Args:
            cmd: Команда в промежуточном представлении
            
        Returns:
            bytes: Байтовое представление команды
        """
        opcode = cmd['opcode']
        operands = cmd['operands']
        
        # Получаем маски для битовых полей
        masks = UVMSpec.get_field_masks(opcode)
        
        # Собираем битовое представление
        value = 0
        
        # Поле A (опкод)
        mask_a, shift_a = masks['A']
        value |= (opcode & mask_a) << shift_a
        
        # Поле B
        mask_b, shift_b = masks['B']
        value |= (operands['B'] & mask_b) << shift_b
        
        # Поле C
        mask_c, shift_c = masks['C']
        value |= (operands['C'] & mask_c) << shift_c
        
        # Определяем размер команды в байтах
        size = UVMSpec.COMMAND_SIZES.get(opcode, 4)
        
        # Конвертируем в байты (little-endian)
        return value.to_bytes(size, byteorder='little')
    
    def encode_program(self, intermediate_repr):
        """
        Кодирует всю программу в машинный код.
        
        Args:
            intermediate_repr: Промежуточное представление программы
            
        Returns:
            bytearray: Бинарное представление программы
        """
        self.binary_data = bytearray()
        self.encoded_commands = []
        
        for cmd in intermediate_repr:
            encoded = self.encode_command(cmd)
            self.encoded_commands.append({
                'command': cmd,
                'bytes': encoded,
                'hex_str': UVMSpec.bytes_to_hex(encoded)
            })
            self.binary_data.extend(encoded)
        
        return self.binary_data
    
    def save_to_file(self, output_path):
        """
        Сохраняет бинарные данные в файл.
        
        Args:
            output_path: Путь к выходному файлу
        """
        with open(output_path, 'wb') as f:
            f.write(self.binary_data)
    
    def print_encoded_commands(self):
        """Выводит закодированные команды в hex формате."""
        print("\n" + "="*60)
        print("БАЙТОВОЕ ПРЕДСТАВЛЕНИЕ КОМАНД:")
        print("="*60)
        
        for i, enc in enumerate(self.encoded_commands, 1):
            cmd = enc['command']
            print(f"\nКоманда {i}: {UVMSpec.OPCODE_NAMES.get(cmd['opcode'], 'UNKNOWN')}")
            print(f"  Исходная: {cmd['description']}")
            print(f"  Байты: {enc['hex_str']}")
    
    def get_statistics(self, output_path):
        """
        Возвращает статистику по ассемблированной программе.
        
        Returns:
            dict: Статистика программы
        """
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        
        return {
            'command_count': len(self.encoded_commands),
            'total_bytes': len(self.binary_data),
            'file_size': file_size,
            'output_file': output_path
        }