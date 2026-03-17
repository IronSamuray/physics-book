#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт генерирует контент задач для main.tex
Не трогает оформление - только условия, ответы и решения.
"""

import os
import re
from pathlib import Path

# === НАСТРОЙКИ ===
TASKS_DIR = Path('tasks')
GENERATED_DIR = Path('generated')
GENERATED_DIR.mkdir(exist_ok=True)

# === ПАРСИНГ ЗАДАЧ ===

def parse_task_file(filepath):
    """Парсит файл с задачами"""
    tasks = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    task_blocks = re.split(r'=== ЗАДАЧА ===', content)
    
    for block in task_blocks[1:]:
        if '=== КОНЕЦ ===' not in block:
            continue
        
        block = block.split('=== КОНЕЦ ===')[0].strip()
        
        task = {
            'rating': 0,
            'condition': '',
            'answer': '',
            'solution': None,
        }
        
        # Парсим рейтинг
        rating_match = re.search(r'РЕЙТИНГ:\s*(\d+)', block)
        if rating_match:
            task['rating'] = int(rating_match.group(1))
        
        # Парсим условие
        condition_match = re.search(r'УСЛОВИЕ:\s*(.+?)(?=ОТВЕТ:|РЕШЕНИЕ:|$)', block, re.DOTALL)
        if condition_match:
            task['condition'] = condition_match.group(1).strip()
        
        # Парсим ответ
        answer_match = re.search(r'ОТВЕТ:\s*(.+?)(?=РЕШЕНИЕ:|$)', block, re.DOTALL)
        if answer_match:
            task['answer'] = answer_match.group(1).strip()
        
        # Парсим решение (опционально)
        solution_match = re.search(r'РЕШЕНИЕ:\s*(.+?)$', block, re.DOTALL)
        if solution_match:
            task['solution'] = solution_match.group(1).strip()
        
        tasks.append(task)
    
    return tasks

def collect_all_tasks():
    """Собирает все задачи из папки tasks/."""
    all_tasks = []
    
    if not TASKS_DIR.exists():
        print(f"Папка {TASKS_DIR} не найдена")
        return all_tasks
    
    for file in sorted(TASKS_DIR.glob('*.txt')):
        print(f"Читаю {file.name}...")
        tasks = parse_task_file(file)
        all_tasks.extend(tasks)
    
    # Сортируем по рейтингу и нумеруем
    all_tasks.sort(key=lambda x: x['rating'])
    for i, task in enumerate(all_tasks, 1):
        task['number'] = i
    
    return all_tasks

# === ГЕНЕРАЦИЯ TEX ФАЙЛОВ ===

def generate_tasks_content(tasks):
    """Генерирует tasks_content.tex с условиями."""
    output = []
    
    for task in tasks:
        latex = r"\problem{%d}{%d}" % (task['number'], task['rating']) + "\n"
        latex += task['condition'] + "\n"
        output.append(latex)
    
    with open(GENERATED_DIR / 'tasks_content.tex', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print("Создан generated/tasks_content.tex")

def generate_answers_content(tasks):
    """Генерирует answers_content.tex с ответами и решениями."""
    output = []
    
    for task in tasks:
        latex = r"\answer{%d}{%s}" % (task['number'], task['answer']) + "\n"
        
        if task['solution']:
            latex += r"\solution{%s}" % task['solution'] + "\n"
        
        output.append(latex)
    
    with open(GENERATED_DIR / 'answers_content.tex', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print("Создан generated/answers_content.tex")

# === MAIN ===

def main():
    print("Генерация контента сборника...\n")
    
    tasks = collect_all_tasks()
    
    if not tasks:
        print("Задачи не найдены!")
        return
    
    print(f"Найдено задач: {len(tasks)}\n")
    
    generate_tasks_content(tasks)
    generate_answers_content(tasks)
    
    print("\n Готово!")
    print(" Теперь открой main.tex и нажми Ctrl+Alt+B")
    print(" PDF сохранится рядом с main.tex")

if __name__ == '__main__':
    main()