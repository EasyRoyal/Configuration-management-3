"""
Содержит константы, структуры данных и утилиты для работы со спецификацией.
"""

class UVMSpec:
    """Спецификация УВМ для Варианта №3."""
    
    # Опкоды команд
    LOAD_CONST = 29    # Загрузка константы
    READ_MEM = 18      # Чтение из памяти
    WRITE_MEM = 9      # Запись в память
    ABS = 25           # Абсолютное значение
    
    # Имена команд для отображения
    OPCODE_NAMES = {
        LOAD_CONST: "LOAD_CONST",
        READ_MEM: "READ_MEM",
        WRITE_MEM: "WRITE_MEM",
        ABS: "ABS"
    }
    
    # Описание команд
    OPCODE_DESCRIPTIONS = {
        LOAD_CONST: "Загрузить константу в регистр",
        READ_MEM: "Прочитать значение из памяти в регистр",
        WRITE_MEM: "Записать значение из регистра в память",
        ABS: "Вычислить абсолютное значение"
    }
    
    # Размеры команд в байтах
    COMMAND_SIZES = {
        LOAD_CONST: 4,
        READ_MEM: 4,
        WRITE_MEM: 4,
        ABS: 4
    }
    
    # Битовые маски для полей
    @staticmethod
    def get_field_masks(opcode):
        """Возвращает маски битовых полей для команды."""
        if opcode == UVMSpec.LOAD_CONST:
            return {
                'A': (0x3F, 0),      # 6 бит, позиция 0
                'B': (0xFFFFF, 6),   # 20 бит, позиция 6
                'C': (0x1F, 26)      # 5 бит, позиция 26
            }
        else:  # READ_MEM, WRITE_MEM, ABS
            return {
                'A': (0x3F, 0),      # 6 бит, позиция 0
                'B': (0x1F, 6),      # 5 бит, позиция 6
                'C': (0x1F, 11)      # 5 бит, позиция 11
            }
    
    @staticmethod
    def validate_command(opcode, operands):
        """Проверяет корректность команды."""
        if opcode not in [UVMSpec.LOAD_CONST, UVMSpec.READ_MEM, 
                         UVMSpec.WRITE_MEM, UVMSpec.ABS]:
            raise ValueError(f"Неизвестный опкод: {opcode}")
        
        if 'B' not in operands or 'C' not in operands:
            raise ValueError(f"Команда требует операнды B и C")
        
        # Проверка диапазонов
        if opcode == UVMSpec.LOAD_CONST:
            if not (0 <= operands['B'] <= 0xFFFFF):
                raise ValueError(f"Константа B={operands['B']} вне диапазона 0..0xFFFFF")
        else:
            if not (0 <= operands['B'] <= 0x1F):
                raise ValueError(f"Адрес B={operands['B']} вне диапазона 0..31")
        
        if not (0 <= operands['C'] <= 0x1F):
            raise ValueError(f"Адрес C={operands['C']} вне диапазона 0..31")
        
        return True
    
    @staticmethod
    def bytes_to_hex(bytes_data):
        """Конвертирует байты в строку hex формата."""
        return ", ".join(f"0x{b:02X}" for b in bytes_data)
    
    @staticmethod
    def get_command_description(opcode, operands):
        """Возвращает текстовое описание команды."""
        name = UVMSpec.OPCODE_NAMES.get(opcode, "UNKNOWN")
        
        if opcode == UVMSpec.LOAD_CONST:
            return f"{name}: Загрузить константу {operands['B']} в регистр R{operands['C']}"
        elif opcode == UVMSpec.READ_MEM:
            return f"{name}: Прочитать из памяти адреса R{operands['C']} в регистр R{operands['B']}"
        elif opcode == UVMSpec.WRITE_MEM:
            return f"{name}: Записать из регистра R{operands['C']} в память адреса R{operands['B']}"
        elif opcode == UVMSpec.ABS:
            return f"{name}: Взять модуль из регистра R{operands['C']}, записать в память адреса R{operands['B']}"
        else:
            return f"{name}: Неизвестная команда"