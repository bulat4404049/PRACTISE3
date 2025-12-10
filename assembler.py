#!/usr/bin/env python3
# assembler.py

import yaml
import argparse
import struct

class Assembler:
    def __init__(self):
        self.opcodes = {
            'load_const': 4,
            'read_mem': 7,
            'write_mem': 2,
            'sqrt': 1
        }
    
    def parse_yaml(self, yaml_file):
        """Парсинг YAML-файла с программой"""
        with open(yaml_file, 'r') as f:
            program = yaml.safe_load(f)
        return program
    
    def assemble_instruction(self, instruction):
        """Ассемблирование одной инструкции"""
        for op, value in instruction.items():
            if op in self.opcodes:
                opcode = self.opcodes[op]
                
                if op == 'load_const':
                    # Команда 4: загрузка константы (2 байта)
                    # Биты 0-2: A=4, Биты 3-15: константа
                    if value < 0 or value > 8191:  # 13 бит
                        raise ValueError(f"Константа {value} вне диапазона 0-8191")
                    
                    # Формат: [AAAAABBB BBBBBBBB]
                    byte1 = (opcode << 5) | (value >> 8) & 0x1F
                    byte2 = value & 0xFF
                    return bytes([byte1, byte2])
                
                elif op == 'read_mem':
                    # Команда 7: чтение из памяти (2 байта)
                    # Биты 0-2: A=7, Биты 3-13: смещение
                    if value < 0 or value > 2047:  # 11 бит
                        raise ValueError(f"Смещение {value} вне диапазона 0-2047")
                    
                    byte1 = (opcode << 5) | (value >> 8) & 0x1F
                    byte2 = value & 0xFF
                    return bytes([byte1, byte2])
                
                elif op == 'write_mem':
                    # Команда 2: запись в память (2 байта)
                    # Биты 0-2: A=2, Биты 3-13: смещение
                    if value < 0 or value > 2047:  # 11 бит
                        raise ValueError(f"Смещение {value} вне диапазона 0-2047")
                    
                    byte1 = (opcode << 5) | (value >> 8) & 0x1F
                    byte2 = value & 0xFF
                    return bytes([byte1, byte2])
                
                elif op == 'sqrt':
                    # Команда 1: sqrt (5 байт)
                    # Биты 0-2: A=1, Биты 3-32: адрес
                    if value < 0 or value > 0x3FFFFFFF:  # 30 бит
                        raise ValueError(f"Адрес {value} вне диапазона 0-1073741823")
                    
                    # Формируем 5 байт
                    byte1 = (opcode << 5) | ((value >> 24) & 0x1F)
                    byte2 = (value >> 16) & 0xFF
                    byte3 = (value >> 8) & 0xFF
                    byte4 = value & 0xFF
                    byte5 = 0x00  # Заполняем нулями
                    return bytes([byte1, byte2, byte3, byte4, byte5])
    
    def assemble(self, program, output_file, test_mode=False):
        """Ассемблирование всей программы"""
        binary_code = b''
        intermediate_rep = []
        
        for i, instr in enumerate(program):
            try:
                binary = self.assemble_instruction(instr)
                binary_code += binary
                
                # Сохраняем промежуточное представление для тестирования
                for op, value in instr.items():
                    intermediate_rep.append({
                        'index': i,
                        'opcode': self.opcodes[op],
                        'operand': value,
                        'bytes': binary.hex()
                    })
                    
                    if test_mode:
                        print(f"Инструкция {i}: {op} {value}")
                        print(f"  Байты: {' '.join([f'0x{b:02X}' for b in binary])}")
                        
            except Exception as e:
                print(f"Ошибка в инструкции {i}: {instr}")
                print(f"Ошибка: {e}")
                return False
        
        # Сохраняем бинарный файл
        with open(output_file, 'wb') as f:
            f.write(binary_code)
        
        # Выводим промежуточное представление в тестовом режиме
        if test_mode:
            print("\n=== Промежуточное представление ===")
            for ir in intermediate_rep:
                print(f"#{ir['index']}: opcode={ir['opcode']}, operand={ir['operand']}, bytes={ir['bytes']}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Ассемблер для УВМ (вариант 26)')
    parser.add_argument('--input', required=True, help='Путь к YAML-файлу с программой')
    parser.add_argument('--output', required=True, help='Путь для сохранения бинарного файла')
    parser.add_argument('--test', action='store_true', help='Режим тестирования')
    
    args = parser.parse_args()
    
    assembler = Assembler()
    
    try:
        # Читаем YAML-программу
        program = assembler.parse_yaml(args.input)
        
        # Ассемблируем
        success = assembler.assemble(program, args.output, args.test)
        
        if success:
            print(f"Программа успешно ассемблирована в {args.output}")
            if args.test:
                print("Режим тестирования завершен")
        else:
            print("Ошибка при ассемблировании")
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()