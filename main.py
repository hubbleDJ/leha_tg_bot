from pathlib import Path
from TgApi import TgApi
from typing import Any
import sqlite3 as sq

import re
import sys
import json
import asyncio

BASE_DIR = Path(__file__).resolve().parent
TG_KEYS_DIR = Path(BASE_DIR, '.keys', 'tg.json')
DB_PATH = Path(BASE_DIR, 'my_db.db')
CHAT_MAIN_ID = -1002588691818

with open(TG_KEYS_DIR, 'r') as f:
    TOKEN = json.load(f)['token']
    
async def db_run_query(query: str) -> Any:
    """Делает запрос в базу данных"""
    
    with sq.connect(DB_PATH) as connect:
        answer = connect.cursor().execute(query).fetchall()
        
    return answer

def create_table_var() -> None:
    """Создает таблицу с переменными"""
    
    query = (
        'create table if not exists vars (\n'
        '\tchat_id integer,\n'
        '\tuser_id integer,\n'
        '\tvar_name text,\n'
        '\tvar_value text\n'
        ')'
    )
    return str(asyncio.run(db_run_query(query)))

def create_var_in_table(chat_id: int, user_id: int, var_name: str, var_value: str):
    """Создает переменную в таблице"""
    
    query = (
        'insert into vars (chat_id, user_id, var_name, var_value) '
            f'values({chat_id}, {user_id}, "{var_name}", "{var_value}")'
    )
    return str(asyncio.run(db_run_query(query)))


def update_var_in_table(chat_id: int, user_id: int, var_name: str, new_value: str):
    """Обновляет переременную в таблице"""
    
    query = (
        f'''update vars set var_value = "{new_value}"\n\t'''
        f'''where chat_id = {chat_id} and user_id = {user_id} and var_name = "{var_name}"'''
    )
    return str(asyncio.run(db_run_query(query)))

def get_var_in_table(chat_id: int, user_id: int, var_name: str):
    """Возвращает значение переменной"""
    
    query = (
        'select var_value from vars\n\t'
        f'''where chat_id = {chat_id} and user_id = {user_id} and var_name = "{var_name}"\n\t'''
        'limit 1'
    )
    return asyncio.run(db_run_query(query))[0][0]
    
def delete_var_in_table(chat_id: int, user_id: int, var_name: str):
    """Удаляет переменную из таблицы"""
    
    query = (
        'delete from vars\n\t'
        f'''where chat_id = {chat_id} and user_id = {user_id} and var_name = "{var_name}"'''
    )
    return str(asyncio.run(db_run_query(query)))

def get_count_var_in_table(chat_id: int, user_id: int, var_name: str) -> int:
    """Возвращает количество переменной в таблице"""
    
    query = (
        'select count(1) from vars\n\t'
        f'''where chat_id = {chat_id} and user_id = {user_id} and var_name = "{var_name}"'''
    )
    return asyncio.run(db_run_query(query))[0][0]

def save_var(chat_id: int, user_id: int, var_name: str, var_value: str):
    """Сохраняет переменную или обновляет ее"""
    
    count_var = get_count_var_in_table(
        chat_id=chat_id,
        user_id=user_id,
        var_name=var_name
    )
    
    if count_var == 0:
        create_var_in_table(
            chat_id=chat_id,
            user_id=user_id,
            var_name=var_name,
            var_value=var_value
        )
    elif count_var == 1:
        update_var_in_table(
            chat_id=chat_id,
            user_id=user_id,
            var_name=var_name,
            new_value=var_value
        )
    else:
        delete_var_in_table(
            chat_id=chat_id,
            user_id=user_id,
            var_name=var_name
        )
        create_var_in_table(
            chat_id=chat_id,
            user_id=user_id,
            var_name=var_name,
            var_value=var_value
        )

def create_table_checkpoint() -> None:
    """Создает таблицу с id сценария пользователей"""
    
    query = (
        'create table if not exists checkpoint (\n'
        '\tchat_id integer,\n'
        '\tuser_id integer,\n'
        '\tscenario_id\n'
        ')'
    )
    return str(asyncio.run(db_run_query(query)))


def get_count_checkpoint_in_table(chat_id: int, user_id: int) -> int:
    """Возвращает количество записей с checkpoint"""
    
    query = (
        'select count(1) from checkpoint\n\t'
        f'''where chat_id = {chat_id} and user_id = {user_id}'''
    )
    return asyncio.run(db_run_query(query))[0][0]


def create_checkpoint_in_table(chat_id: int, user_id: int, scenario_id: int):
    """Создает checkpoint в таблице"""
    
    query = (
        'insert into checkpoint (chat_id, user_id, scenario_id) '
            f'values({chat_id}, {user_id}, {scenario_id})'
    )
    return str(asyncio.run(db_run_query(query)))


def update_checkpoint_in_table(chat_id: int, user_id: int, scenario_id: int):
    """Обновляет checkpoint в таблице"""
    
    query = (
        f'''update checkpoint set scenario_id = {scenario_id}\n\t'''
        f'''where chat_id = {chat_id} and user_id = {user_id}'''
    )
    return str(asyncio.run(db_run_query(query)))


def delete_checkpoint_in_table(chat_id: int, user_id: int):
    """Удаляет checkpoint из таблицы"""
    
    query = (
        'delete from checkpoint\n\t'
        f'''where chat_id = {chat_id} and user_id = {user_id}'''
    )
    return str(asyncio.run(db_run_query(query)))

def get_checkpoint_in_table(chat_id: int, user_id: int) -> int:
    """Возвращает id сцерания в котором сейчас пользователь"""
    
    query = (
        'select scenario_id from checkpoint\n\t'
        f'''where chat_id = {chat_id} and user_id = {user_id}\n\t'''
        'limit 1'
    )
    return asyncio.run(db_run_query(query))[0][0]

def get_checkpoint_id(chat_id: int, user_id: int) -> int:
    """"""
    
    if get_count_checkpoint_in_table(chat_id=chat_id, user_id=user_id) == 0:
        return 0
    else:
        return get_checkpoint_in_table(chat_id=chat_id, user_id=user_id)
        

def save_checkpoint(chat_id: int, user_id: int, scenario_id: int):
    """Сохраняет checkpoint"""
    
    count_checkpoint = get_count_checkpoint_in_table(
        user_id=user_id,
        chat_id=chat_id
    )
    if count_checkpoint == 0:
        create_checkpoint_in_table(
            chat_id=chat_id,
            user_id=user_id,
            scenario_id=scenario_id
        )
    elif count_checkpoint == 1:
        update_checkpoint_in_table(
            chat_id=chat_id,
            user_id=user_id,
            scenario_id=scenario_id
        )
    else:
        delete_checkpoint_in_table(
            chat_id=chat_id,
            user_id=user_id
        )
        create_checkpoint_in_table(
            chat_id=chat_id,
            user_id=user_id,
            scenario_id=scenario_id
        )

def hello(message: dict): pass

def processing_problem(message: dict): 
    """"""
    
    save_var(
        chat_id=message['chat']['id'],
        user_id=message['from']['id'],
        var_name='problem',
        var_value=message['text']
    )
    
def processing_contact(message: dict):
    """"""
    
    save_var(
        chat_id=message['chat']['id'],
        user_id=message['from']['id'],
        var_name='contact',
        var_value=message['text']
    )
    
    text_message = (
        'Новове сообщение\n'
        f'''Контакт: {get_var_in_table(chat_id=message['chat']['id'], user_id=message['from']['id'], var_name='contact')}\n'''
        f'''Проблема: {get_var_in_table(chat_id=message['chat']['id'], user_id=message['from']['id'], var_name='problem')}\n\n'''
        f'''tg_info: {message['from']}'''
    )
    
    asyncio.run(TG_BOT.send_message(
        text=text_message,
        chat_id=CHAT_MAIN_ID
    ))


SCENARIOS = {
    0: {
        "text": "Привет! Опиши, что у тебя случилось в одном сообщении",
        "next_scenario": 1,
        "function": hello
    },
    1: {
        "text": "Понял. Теперь скажи, как с тобой связаться. Оставь контакт, по которому можно с тобой связаться в одном сообщении",
        "next_scenario": 2,
        "function": processing_problem
    },
    2: {
        "text": "Хорошо. Мы с тобой обязатеьно свяжeмся. Если, у тебя есть еще вопросы/проблемы - пиши их тут",
        "next_scenario": 3,
        "function": processing_contact
    },
    3: {
        "text": "Понял. Теперь скажи, как с тобой связаться. Оставь контакт, по которому можно с тобой связаться в одном сообщении ",
        "next_scenario": 2,
        "function": processing_problem
    }
}


def main() -> None:
    while True:
        messages = asyncio.run(TG_BOT.get_messages())['messages']
        if len(messages) > 0:
            for message in messages:
                if 'text' in message and message['chat']['id'] == message['from']['id']:
                    if message['text'] == '/start':
                        save_checkpoint(
                            chat_id=message['chat']['id'],
                            user_id=message['from']['id'],
                            scenario_id=0
                        )
                    
                    scenario_id = get_checkpoint_id(
                        chat_id=message['chat']['id'],
                        user_id=message['from']['id']
                    )
                    scenario = SCENARIOS[scenario_id]
                    
                    scenario['function'](message)
                    save_checkpoint(
                        chat_id=message['chat']['id'],
                        user_id=message['from']['id'],
                        scenario_id=scenario['next_scenario']
                    )
                    asyncio.run(TG_BOT.send_message(
                        text=scenario['text'],
                        chat_id=message['chat']['id']
                    ))

if __name__ == '__main__':
    create_table_var()
    create_table_checkpoint()
    TG_BOT = TgApi(TOKEN)
    main()