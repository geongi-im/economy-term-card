import os
from datetime import datetime
from image_processor import ImageProcessor
from database_manager import DatabaseManager

def main():
    # output 폴더 초기화
    os.makedirs("output", exist_ok=True)
    os.chmod("output", 0o777)  # 폴더 권한을 777로 설정

    processor = ImageProcessor()
    db_manager = DatabaseManager()
    term_list = db_manager.get_random_term()

    for no, term in enumerate(term_list):
        no = f"{no + 1:02}"
        idx = term[0]
        title = term[1]
        short_content = term[2]
        long_content = term[3]

        today = datetime.now().strftime('%Y%m%d')
        output_path = f"output/{today}_{no}.png"

        processor.create_card(
            no=no,
            title=title,
            short_content = short_content,
            long_content = long_content,
            output_path=output_path
        )

        db_manager.update_term_list(idx, output_path)

if __name__ == "__main__":
    main()