import os
from datetime import datetime
from image_processor import ImageProcessor
from database_manager import DatabaseManager
from utils.instagram_post import InstagramAPI
from utils.telegram_util import TelegramUtil
from utils.ncafe_post import NaverCafeAPI
from utils.api_util import ApiUtil, ApiError
from utils.logger_util import LoggerUtil
from dotenv import load_dotenv

load_dotenv()

def get_image_url(file_path):
    """로컬 이미지 파일의 URL을 생성"""
    # 여기에 실제 이미지가 호스팅되는 베이스 URL을 입력해야 합니다
    base_url = f'{os.getenv("DOMAIN_URL")}/output'
    return f"{base_url}/{os.path.basename(file_path)}"

def get_unique_filename(output_path):
    """중복되지 않는 파일명 생성"""
    if not os.path.exists(output_path):
        return output_path
    
    base_name, extension = os.path.splitext(output_path)
    index = 1
    
    while True:
        new_path = f"{base_name}({index}){extension}"
        if not os.path.exists(new_path):
            return new_path
        index += 1

def main():
    # output 폴더 초기화
    os.makedirs("output", exist_ok=True)
    os.chmod("output", 0o777)  # 폴더 권한을 777로 설정

    processor = ImageProcessor()
    db_manager = DatabaseManager(db_path='term.db')
    telegram = TelegramUtil()
    api_util = ApiUtil()
    logger = LoggerUtil().get_logger()
    term_list = db_manager.get_random_term()
    image_paths = []  # 생성된 이미지 경로를 저장할 리스트
    term_updates = []  # DB 업데이트를 위한 정보를 저장할 리스트
    terms = []  # 용어 목록을 저장할 리스트

    # 표지 이미지 경로 추가
    main_image_path = "output/main.png"
    
    # 표지 이미지가 없으면 img/main.png를 output 폴더로 복사
    if not os.path.exists(main_image_path):
        import shutil
        shutil.copy2("img/main.png", main_image_path)
    
    # 표지 이미지를 첫 번째로 추가
    image_paths.append(main_image_path)

    # 이미지 생성
    for no, data in enumerate(term_list):
        no = f"{no + 1:02}"
        idx = data[0]
        term = data[1]
        short_description = data[2]
        description = data[3]
        
        # 용어 목록에 추가
        terms.append(term)

        today = datetime.now().strftime('%Y%m%d')
        base_output_path = f"output/{today}_{no}.png"
        
        # 중복 파일명 처리
        output_path = get_unique_filename(base_output_path)

        # 이미지 생성
        processor.create_card(
            no=no,
            term=term,
            short_description=short_description,
            description=description,
            output_path=output_path
        )
        
        # 생성된 이미지 경로와 DB 업데이트 정보 저장
        image_paths.append(output_path)
        term_updates.append((idx, output_path))

        print(f"이미지 생성 완료: {output_path}")

    # 이미지 URL 생성 (표지 이미지 포함)
    # image_urls = [get_image_url(path) for path in image_paths]

    # API 전송
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 모든 용어를 해시태그로 사용
    term_hashtags = ' '.join([f"<a href=\"#\">#{term}</a>" for term in terms])
    
    try:
        logger.info("API 포스트 생성 시작")
        api_util.create_post(
            title=f"{today} 오늘의 경제용어",
            content=f"""<strong><h3>{today} 우리 아이가 알아야 할 오늘의 경제용어</h3></strong><br>
            <p>
                {term_hashtags} 
                <a href="#">#경제교육</a> 
                <a href="#">#아이와함께</a> 
                <a href="#">#오늘의경제</a> 
                <a href="#">#MQWAY</a> 
            </p>""",
            category="경제용어",
            writer="admin",
            image_paths=image_paths
        )
        logger.info("API 포스트 생성 완료")
    except ApiError as e:
        error_message = f"❌ API 오류 발생\n\n{e.message}"
        telegram.send_test_message(error_message)
        logger.error(f"API 포스트 생성 오류: {e.message}")

    # DB 업데이트
    for idx, output_path in term_updates:
        db_manager.update_term_list(idx, output_path)
        print(f"DB 업데이트 완료: ID {idx}")

if __name__ == "__main__":
    main()