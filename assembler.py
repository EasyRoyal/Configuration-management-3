#!/usr/bin/env python3
"""
Ассемблер УВМ - преобразует YAML программу в промежуточное представление
"""

import yaml
from typing import List, Dict, Any

class Assembler:
    """Ассемблер для Учебной Виртуальной Машины (Вариант 3)"""
    
    # Коды операций из спецификации Варианта 3
    OPCODES = {
        "LOAD": 29,   # Загрузка константы
        "READ": 18,   # Чтение из памяти
        "WRITE": 9,   # Запись в память
        "ABS": 25,    # Абсолютное значение
    }
    
    def __init__(self):
        self.intermediate_code = []
    
    def assemble(self, input_file: str) -> List[Dict[str, Any]]:
        """
        Ассемблирует YAML программу в промежуточное представление
        
        Args:
            input_file: Путь к YAML файлу
            
        Returns:
            List[Dict]: Промежуточное представление команд
        """
        print(f"📖 Чтение файла: {input_file}")
        
        try:
            # Загружаем YAML
            with open(input_file, 'r', encoding='utf-8') as f:
                program_data = yaml.safe_load(f)
            
            print(f"📄 Загружено YAML данных")
            
            if not program_data:
                raise ValueError("YAML файл пуст")
            
            if 'program' not in program_data:
                raise ValueError("YAML файл должен содержать ключ 'program'")
            
            self.intermediate_code = []
            
            # Обрабатываем каждую команду
            for i, cmd_dict in enumerate(program_data['program']):
                print(f"  🔨 Обработка команды {i}: {cmd_dict}")
                intermediate_cmd = self._parse_command(cmd_dict, i)
                self.intermediate_code.append(intermediate_cmd)
            
            return self.intermediate_code
            
        except yaml.YAMLError as e:
            raise ValueError(f"Ошибка парсинга YAML: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка ассемблирования: {e}")
    
    def _parse_command(self, cmd_dict: Dict, line_num: int) -> Dict[str, Any]:
        """
        Парсит одну команду из YAML в промежуточное представление
        """
        if 'command' not in cmd_dict:
            raise ValueError(f"Строка {line_num}: отсутствует ключ 'command'")
        
        command = cmd_dict['command'].upper()
        
        if command not in self.OPCODES:
            raise ValueError(f"Строка {line_num}: неизвестная команда '{command}'")
        
        opcode = self.OPCODES[command]
        intermediate = {"opcode": opcode, "command": command}
        
        # Проверяем аргументы в зависимости от команды
        if command == "LOAD":
            # LOAD требует value и register
            if 'value' not in cmd_dict:
                raise ValueError(f"Строка {line_num}: команда LOAD требует значение 'value'")
            if 'register' not in cmd_dict:
                raise ValueError(f"Строка {line_num}: команда LOAD требует регистр 'register'")
            intermediate['value'] = cmd_dict['value']
            intermediate['register'] = cmd_dict['register']
            
        elif command == "READ":
            # READ требует dest_register и addr_register
            if 'dest_register' not in cmd_dict:
                raise ValueError(f"Строка {line_num}: команда READ требует 'dest_register'")
            if 'addr_register' not in cmd_dict:
                raise ValueError(f"Строка {line_num}: команда READ требует 'addr_register'")
            intermediate['dest_register'] = cmd_dict['dest_register']
            intermediate['addr_register'] = cmd_dict['addr_register']
            
        elif command == "WRITE":
            # WRITE требует addr_register и src_register
            if 'addr_register' not in cmd_dict:
                raise ValueError(f"Строка {line_num}: команда WRITE требует 'addr_register'")
            if 'src_register' not in cmd_dict:
                raise ValueError(f"Строка {line_num}: команда WRITE требует 'src_register'")
            intermediate['addr_register'] = cmd_dict['addr_register']
            intermediate['src_register'] = cmd_dict['src_register']
            
        elif command == "ABS":
            # ABS требует addr_register и src_register
            if 'addr_register' not in cmd_dict:
                raise ValueError(f"Строка {line_num}: команда ABS требует 'addr_register'")
            if 'src_register' not in cmd_dict:
                raise ValueError(f"Строка {line_num}: команда ABS требует 'src_register'")
            intermediate['addr_register'] = cmd_dict['addr_register']
            intermediate['src_register'] = cmd_dict['src_register']
        
        return intermediate
    
    def _parse_command_test(self, cmd_dict: Dict, line_num: int) -> Dict[str, Any]:
        """Тестовая версия для демонстрации (без изменения YAML)"""
        return self._parse_command(cmd_dict, line_num)
    
    def get_intermediate_code(self) -> List[Dict[str, Any]]:
        """Возвращает промежуточное представление"""
        return self.intermediate_code