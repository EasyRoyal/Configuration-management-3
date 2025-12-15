"""
Парсинг YAML файлов и создание промежуточного представления.
"""

import yaml
import sys
from spec import UVMSpec

class YamlParser:
    """Парсер YAML файлов для УВМ."""
    
    def __init__(self):
        self.intermediate_repr = []
        self.errors = []
    
    def parse(self, yaml_path):
        """
        Парсит YAML файл и создает промежуточное представление.
        
        Args:
            yaml_path: Путь к YAML файлу
            
        Returns:
            list: Промежуточное представление программы
            
        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если структура YAML некорректна
        """
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            self.intermediate_repr = []
            self.errors = []
            
            # Проверяем структуру YAML
            if data is None:
                raise ValueError("YAML файл пуст")
            
            if 'commands' not in data:
                raise ValueError("YAML файл должен содержать ключ 'commands'")
            
            # Парсим команды
            for cmd_idx, cmd_data in enumerate(data['commands'], 1):
                try:
                    self._parse_command(cmd_idx, cmd_data)
                except Exception as e:
                    self.errors.append(f"Команда {cmd_idx}: {e}")
            
            # Проверяем наличие ошибок
            if self.errors:
                error_msg = "\n".join(self.errors)
                raise ValueError(f"Ошибки при парсинге:\n{error_msg}")
            
            print(f"✓ Успешно загружено {len(self.intermediate_repr)} команд")
            return self.intermediate_repr
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл {yaml_path} не найден")
        except yaml.YAMLError as e:
            raise ValueError(f"Ошибка парсинга YAML: {e}")
    
    def _parse_command(self, cmd_idx, cmd_data):
        """Парсит одну команду."""
        # Проверяем обязательные поля
        if 'opcode' not in cmd_data:
            raise ValueError("Отсутствует поле 'opcode'")
        
        if 'operands' not in cmd_data:
            raise ValueError("Отсутствует поле 'operands'")
        
        opcode = cmd_data['opcode']
        operands = cmd_data['operands']
        
        # Валидируем команду
        UVMSpec.validate_command(opcode, operands)
        
        # Добавляем в промежуточное представление
        self.intermediate_repr.append({
            'index': cmd_idx,
            'opcode': opcode,
            'operands': operands,
            'description': UVMSpec.get_command_description(opcode, operands)
        })
    
    def print_intermediate(self, intermediate_repr):
        """Выводит промежуточное представление в читаемом формате."""
        print("\n" + "="*60)
        print("ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ ПРОГРАММЫ:")
        print("="*60)
        
        for cmd in intermediate_repr:
            print(f"\nКоманда {cmd['index']}:")
            print(f"  Опкод: {cmd['opcode']} ({UVMSpec.OPCODE_NAMES.get(cmd['opcode'], 'UNKNOWN')})")
            print(f"  Операнды: {cmd['operands']}")
            print(f"  Описание: {cmd['description']}")
        
        print("\n" + "="*60)