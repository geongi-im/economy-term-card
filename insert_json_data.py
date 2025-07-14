from datetime import datetime
import json
import os
from database_manager import DatabaseManager
from utils.logger_util import LoggerUtil

# DB 및 로거 초기화
db_path = 'term.db'
db = DatabaseManager(db_path=db_path)
logger = LoggerUtil().get_logger()

# JSON 파일 경로
json_path = os.path.join('source', '250714_3.json')

# 사용자 입력 플래그
global_skip = False
global_overwrite = False

def get_existing_term(term):
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT idx, short_description, description FROM term_list WHERE term = ?', (term,))
        return cursor.fetchone()

def insert_term(term, short_desc, desc):
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO term_list (term, short_description, description) VALUES (?, ?, ?)''', (term, short_desc, desc))
        conn.commit()
        logger.info(f"'{term}' 항목이 새로 추가되었습니다.")

def update_term(idx, term, short_desc, desc):
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE term_list SET short_description = ?, description = ? WHERE idx = ?''', (short_desc, desc, idx))
        conn.commit()
        logger.info(f"'{term}' 항목이 덮어쓰기(업데이트)되었습니다.")

def main():
    global global_skip, global_overwrite
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for item in data:
        term = item['term']
        short_desc = item['short_description']
        desc = item['description']
        
        existing = get_existing_term(term)
        if existing:
            idx, old_short, old_desc = existing
            print(f"\n[중복] '{term}' 키워드가 이미 존재합니다.")
            print(f"- 기존 요약: {old_short}")
            print(f"- 기존 설명: {old_desc}")
            print(f"- 새 요약: {short_desc}")
            print(f"- 새 설명: {desc}")
            
            if global_skip:
                logger.info(f"'{term}' 항목을 건너뜀 (전체 건너뛰기 설정)")
                continue
            if global_overwrite:
                update_term(idx, term, short_desc, desc)
                continue
            
            print("[1] 건너뛰기  [2] 덮어쓰기  [3] 이후 모두 건너뛰기  [4] 이후 모두 덮어쓰기")
            choice = input("선택: ").strip()
            if choice == '1':
                logger.info(f"'{term}' 항목을 건너뜀 (사용자 선택)")
                continue
            elif choice == '2':
                update_term(idx, term, short_desc, desc)
            elif choice == '3':
                global_skip = True
                logger.info(f"'{term}' 항목을 건너뜀 (이후 모두 건너뛰기 설정)")
                continue
            elif choice == '4':
                global_overwrite = True
                update_term(idx, term, short_desc, desc)
            else:
                print("잘못된 입력입니다. 기본적으로 건너뜁니다.")
                logger.info(f"'{term}' 항목을 건너뜀 (잘못된 입력)")
                continue
        else:
            insert_term(term, short_desc, desc)

if __name__ == '__main__':
    main()
