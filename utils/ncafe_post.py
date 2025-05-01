import os
from urllib.request import urlopen
import urllib.parse
import requests
from dotenv import load_dotenv
import sys
import time

# .env 파일 로드
load_dotenv()

class NaverCafeAPI:
    def __init__(self):
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
        self.access_token = os.getenv('NAVER_ACCESS_TOKEN')
        self.refresh_token = os.getenv('NAVER_REFRESH_TOKEN')

    def get_access_token(self):
        if not self.access_token:
            self.refresh_access_token()
        else:
            # 토큰이 있어도 유효한지 확인
            if not self.is_token_valid():
                self.refresh_access_token()
        return self.access_token

    def is_token_valid(self):
        # 토큰 유효성 검사 (예: 간단한 API 호출)
        url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        return response.status_code == 200

    def refresh_access_token(self):
        url = "https://nid.naver.com/oauth2.0/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            token_info = response.json()
            
            # 새로운 토큰 저장
            self.access_token = token_info['access_token']
            if 'refresh_token' in token_info:
                self.refresh_token = token_info['refresh_token']
            
            # .env 파일 업데이트
            self.update_env_file()
            
            print("액세스 토큰이 갱신되었습니다.")
                
        except requests.RequestException as e:
            print(f"토큰 갱신 오류: {e}")
            print("리프레시 토큰이 만료되었거나 인증 정보가 잘못되었을 수 있습니다.")
            print("네이버 개발자 센터에서 새로운 토큰을 발급받아 .env 파일을 업데이트해주세요.")
            sys.exit(1)

    def update_env_file(self):
        """토큰 정보로 .env 파일 업데이트"""
        env_path = '.env'
        
        # 현재 .env 파일 내용 읽기
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        else:
            lines = []

        # 토큰 업데이트를 위한 새로운 내용
        new_content = {}
        for line in lines:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                new_content[key] = value

        # 새로운 토큰 값 업데이트
        new_content['NAVER_ACCESS_TOKEN'] = self.access_token
        if self.refresh_token:
            new_content['NAVER_REFRESH_TOKEN'] = self.refresh_token

        # 파일에 새로운 내용 쓰기
        with open(env_path, 'w', encoding='utf-8') as file:
            for key, value in new_content.items():
                file.write(f"{key}={value}\n")
    
    def write_cafe_post(self, menu_id, subject, content, image_paths):
        url = f"https://openapi.naver.com/v1/cafe/{os.getenv('NAVER_CAFE_ID')}/menu/{menu_id}/articles"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}"
        }
        
        # 여러 이미지 파일 처리
        files = {}
        for idx, image_path in enumerate(image_paths):
            try:
                with open(image_path, 'rb') as image_file:
                    files[f'image{idx + 1}'] = (
                        os.path.basename(image_path),
                        image_file.read(),
                        'image/png'
                    )
            except FileNotFoundError:
                print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
                continue
            except Exception as e:
                print(f"이미지 처리 중 오류 발생: {e}")
                continue
        
        data = {
            "subject": urllib.parse.quote(subject),
            "content": urllib.parse.quote(content)
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, files=files)
            time.sleep(0.5)  # API 요청 후 0.5초 대기
            
            if response.status_code == 200:
                print("글 작성 성공:")
                print(response.text)
                return True
            else:
                print(f"오류 발생: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"요청 중 오류 발생: {e}")
            return False


def main():
    naver_cafe_api = NaverCafeAPI()
    # access_token = naver_cafe_api.get_access_token()
    # print(f"현재 액세스 토큰: {access_token}")

    result = naver_cafe_api.write_cafe_post(1, "테스트 제목", "테스트 내용", ["output/20241211_01_14.png"])
    print(f"결과: {result}")
if __name__ == "__main__":
    main()
