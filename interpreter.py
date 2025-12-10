#!/usr/bin/env python3
# interpreter.py

import struct
import csv
import argparse
import math
from collections import deque

class UVMInterpreter:
    def __init__(self):
        self.data_memory = [0] * 65536  # Память данных (64K слов)
        self.stack = deque()
        self.pc = 0  # Счетчик команд
        self.running = True
        
    def load_program(self, program_file):
        """Загрузка бинарной программы"""
        with open(program_file, 'rb') as f:
            self.program = f.read()
        return len(self.program)
    
    def decode_instruction(self):
        """Декодирование текущей инструкции"""
        if self.pc >= len(self.program):
            return None, None
        
        # Читаем первый байт для определения типа команды
        first_byte = self.program[self.pc]
        opcode = (first_byte >> 5) & 0x07  # Биты 0-2
        
        if opcode == 4:  # load_const
            # 2-байтовая команда
            if self.pc + 2 > len(self.program):
                return None, None
            second_byte = self.program[self.pc + 1]
            operand = ((first_byte & 0x1F) << 8) | second_byte
            return 4, operand
        
        elif opcode == 7:  # read_mem
            # 2-байтовая команда
            if self.pc + 2 > len(self.program):
                return None, None
            second_byte = self.program[self.pc + 1]
            operand = ((first_byte & 0x1F) << 8) | second_byte
            return 7, operand
        
        elif opcode == 2:  # write_mem
            # 2-байтовая команда
            if self.pc + 2 > len(self.program):
                return None, None
            second_byte = self.program[self.pc + 1]
            operand = ((first_byte & 0x1F) << 8) | second_byte
            return 2, operand
        
        elif opcode == 1:  # sqrt
            # 5-байтовая команда
            if self.pc + 5 > len(self.program):
                return None, None
            
            # Собираем 30-битный операнд
            b1 = self.program[self.pc]
            b2 = self.program[self.pc + 1]
            b3 = self.program[self.pc + 2]
            b4 = self.program[self.pc + 3]
            
            operand = ((b1 & 0x1F) << 24) | (b2 << 16) | (b3 << 8) | b4
            return 1, operand
        
        return None, None
    
    def execute_instruction(self, opcode, operand):
        """Выполнение одной инструкции"""
        if opcode == 4:  # load_const
            self.stack.append(operand)
            self.pc += 2
            
        elif opcode == 7:  # read_mem
            if not self.stack:
                raise Exception("Стек пуст для чтения")
            
            addr = self.stack.pop() + operand
            if 0 <= addr < len(self.data_memory):
                value = self.data_memory[addr]
                self.stack.append(value)
            else:
                raise Exception(f"Неверный адрес памяти: {addr}")
            self.pc += 2
            
        elif opcode == 2:  # write_mem
            if not self.stack:
                raise Exception("Стек пуст для записи")
            
            value = self.stack.pop()
            if not self.stack:
                raise Exception("Стек пуст для адреса")
            
            addr = self.stack.pop() + operand
            if 0 <= addr < len(self.data_memory):
                self.data_memory[addr] = value
            else:
                raise Exception(f"Неверный адрес памяти: {addr}")
            self.pc += 2
            
        elif opcode == 1:  # sqrt
            if not self.stack:
                raise Exception("Стек пуст для sqrt")
            
            value = self.stack.pop()
            if value < 0:
                raise Exception("Корень из отрицательного числа")
            
            result = int(math.sqrt(value))
            
            if 0 <= operand < len(self.data_memory):
                self.data_memory[operand] = result
            else:
                raise Exception(f"Неверный адрес памяти: {operand}")
            self.pc += 5
            
        else:
            self.running = False
    
    def run(self):
        """Основной цикл интерпретации"""
        while self.running and self.pc < len(self.program):
            opcode, operand = self.decode_instruction()
            if opcode is None:
                break
            
            try:
                self.execute_instruction(opcode, operand)
            except Exception as e:
                print(f"Ошибка выполнения по адресу {self.pc}: {e}")
                break
    
    def dump_memory(self, filename, mem_range):
        """Создание дампа памяти в CSV"""
        start, end = map(int, mem_range.split('-'))
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['address', 'value'])
            
            for addr in range(start, min(end + 1, len(self.data_memory))):
                writer.writerow([addr, self.data_memory[addr]])
        
        print(f"Дамп памяти сохранен в {filename} (адреса {start}-{end})")

def main():
    parser = argparse.ArgumentParser(description='Интерпретатор УВМ (вариант 26)')
    parser.add_argument('--input', required=True, help='Файл с бинарной программой')
    parser.add_argument('--dump', required=True, help='Файл для дампа памяти (CSV)')
    parser.add_argument('--range', required=True, help='Диапазон адресов (например, 0-100)')
    
    args = parser.parse_args()
    
    # Создаем интерпретатор
    interpreter = UVMInterpreter()
    
    try:
        # Загружаем программу
        prog_len = interpreter.load_program(args.input)
        print(f"Загружена программа длиной {prog_len} байт")
        
        # Выполняем программу
        interpreter.run()
        print("Программа выполнена")
        
        # Создаем дамп памяти
        interpreter.dump_memory(args.dump, args.range)
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()