# 경제 용어 카드 생성기

경제 용어 카드 생성기는 데이터베이스에서 경제 용어를 랜덤하게 선택하여 이미지 카드로 생성하고, 생성된 이미지를 API를 통해 웹에 게시하는 자동화 프로그램입니다.

## 주요 기능

- 데이터베이스에서 랜덤 경제 용어 선택
- 선택한 용어로 시각적으로 매력적인 이미지 카드 생성
- 생성된 이미지를 웹 API로 전송하여 게시글 자동 등록
- 오류 발생 시 텔레그램을 통한 알림 메시지 전송
- 이미지 생성 및 전송 결과 로깅

## 프로젝트 구조

```
economy-term-card/
├── main.py                  # 메인 실행 파일
├── image_processor.py       # 이미지 카드 생성 클래스
├── database_manager.py      # 데이터베이스 관리 클래스
├── term.db                  # SQLite 데이터베이스 파일
├── utils/                   # 유틸리티 모듈 폴더
│   ├── api_util.py          # API 통신 유틸리티
│   ├── logger_util.py       # 로깅 유틸리티
│   ├── telegram_util.py     # 텔레그램 메시지 전송 유틸리티
│   └── ...
├── img/                     # 이미지 리소스 폴더
│   ├── background_card.png  # 카드 배경 이미지
│   └── main.png             # 표지 이미지
├── fonts/                   # 폰트 파일 폴더
├── output/                  # 생성된 이미지 저장 폴더
└── logs/                    # 로그 파일 저장 폴더
```

## 필요 사항

- Python 3.7 이상
- 필요 패키지: PIL (Pillow), sqlite3, requests, python-dotenv 등

## 설치 방법

1. 저장소 클론:
```bash
git clone https://github.com/yourusername/economy-term-card.git
cd economy-term-card
```

2. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 패키지 설치:
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정:
`.env` 파일을 생성하고 다음 내용을 추가합니다:
```
DOMAIN_URL=https://your-domain.com
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

## 사용 방법

1. 데이터베이스 설정
   - 데이터베이스 형식: `idx`, `term`, `short_description`, `description`, `file_name`, `open_yn`, `reg_date`

2. 실행하기
```bash
python main.py
```

3. 결과
   - 생성된 이미지는 `output/` 폴더에 저장됩니다.
   - 로그 파일은 `logs/` 폴더에 날짜별로 저장됩니다.
   - 이미지와 함께 API로 생성된 게시글은 지정된 웹사이트에 등록됩니다.

## 작동 방식

1. `main.py`가 실행되면 데이터베이스에서 랜덤으로 3개의 경제 용어를 선택합니다.
2. 선택된 각 용어에 대해 `image_processor.py`를 사용하여 이미지 카드를 생성합니다.
3. 생성된 이미지를 `output/` 폴더에 저장합니다.
4. 생성된 이미지들을 포함한 게시글을 API를 통해 웹사이트에 등록합니다.
5. 각 용어의 데이터베이스 레코드를 업데이트하여 사용됨을 표시합니다.
6. 오류 발생 시 텔레그램을 통해 알림을 보냅니다.
