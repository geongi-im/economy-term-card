import os
from datetime import datetime
from image_processor import ImageProcessor
from database_manager import DatabaseManager
from instagram_post import InstagramAPI
from telegram_util import TelegramUtil
from dotenv import load_dotenv

load_dotenv()

def get_image_url(file_path):
    """로컬 이미지 파일의 URL을 생성"""
    # 여기에 실제 이미지가 호스팅되는 베이스 URL을 입력해야 합니다
    base_url = f'{os.getenv("DOMAIN_URL")}/output'
    return f"{base_url}/{os.path.basename(file_path)}"

def main():
    # output 폴더 초기화
    os.makedirs("output", exist_ok=True)
    os.chmod("output", 0o777)  # 폴더 권한을 777로 설정

    processor = ImageProcessor()
    db_manager = DatabaseManager()
    instagram_api = InstagramAPI()
    telegram = TelegramUtil()
    
    term_list = db_manager.get_random_term()
    image_paths = []  # 생성된 이미지 경로를 저장할 리스트
    term_updates = []  # DB 업데이트를 위한 정보를 저장할 리스트

    # 표지 이미지 경로 추가
    main_image_path = "output/main.png"
    
    # 표지 이미지가 없으면 img/main.png를 output 폴더로 복사
    if not os.path.exists(main_image_path):
        import shutil
        shutil.copy2("img/main.png", main_image_path)
    
    # 표지 이미지를 첫 번째로 추가
    image_paths.append(main_image_path)

    # 이미지 생성
    for no, term in enumerate(term_list):
        no = f"{no + 1:02}"
        idx = term[0]
        title = term[1]
        short_content = term[2]
        long_content = term[3]

        today = datetime.now().strftime('%Y%m%d')
        output_path = f"output/{today}_{no}.png"

        # 이미지 생성
        processor.create_card(
            no=no,
            title=title,
            short_content=short_content,
            long_content=long_content,
            output_path=output_path
        )
        
        # 생성된 이미지 경로와 DB 업데이트 정보 저장
        image_paths.append(output_path)
        term_updates.append((idx, output_path))

        print(f"이미지 생성 완료: {output_path}")

    # 이미지 URL 생성 (표지 이미지 포함)
    image_urls = [get_image_url(path) for path in image_paths]    
    
    # Instagram 포스팅
    try:
        caption = f"""우리 아이가 알아야 할 오늘의 경제용어

{' '.join([f'#{term[1]}' for term in term_list])} #MQway #경제교육 #아이와함께 #오늘의경제"""
        
        result = instagram_api.post_image(image_urls, caption=caption)
        
        if result["success"]:
            print("Instagram 포스팅 성공!")
            print(f"Post ID: {result['post_id']}")
            
            # DB 업데이트
            for idx, output_path in term_updates:
                db_manager.update_term_list(idx, output_path)
                print(f"DB 업데이트 완료: ID {idx}")
                
            # Instagram 포스팅 성공 후 텔레그램으로 이미지 전송
            try:
                telegram_caption = f"{datetime.now().strftime('%Y-%m-%d')} 경제용어카드 포스팅 완료\n\n{caption}"
                telegram.send_multiple_photo(image_paths, caption=telegram_caption)
                print("텔레그램 전송 완료!")
            except Exception as e:
                print(f"텔레그램 전송 실패: {str(e)}")
                
        else:
            print(f"Instagram 포스팅 실패: {result['error']}")
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    main()