import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
from utils.logger_util import LoggerUtil

class ImageProcessor:
    def __init__(self):
        """이미지 카드 생성기 초기화"""
        self.background_path = os.path.join('img', 'background_card.png')
        self.logger = LoggerUtil().get_logger()

    def _get_unique_filename(self, base_path):
        """파일명이 중복될 경우 인덱스를 붙여 고유한 파일명 생성"""
        if not os.path.exists(base_path):
            return base_path
        
        base, ext = os.path.splitext(base_path)
        index = 1
        new_path = f"{base}_{index}{ext}"
        
        while os.path.exists(new_path):
            index += 1
            new_path = f"{base}_{index}{ext}"
        
        return new_path
    
    def _draw_text(self, draw, text, font, img_width, start_y, fill):
        """한 줄의 텍스트를 이미지 중앙에 그리기"""
        # 텍스트의 너비 계산
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        
        # 중앙 정렬을 위한 x 좌표 계산
        x_position = (img_width - text_width) // 2
        
        # 텍스트 그리기
        draw.text((x_position, start_y), text, font=font, fill=fill)
        
    def _draw_multiline_text(self, draw, text, font, img_width, start_y, fill):
        """줄바꿈된 텍스트를 이미지 중앙에 그리기"""
        lines = text.split('\n')  # 이미 줄바꿈된 텍스트를 라인별로 분리
        current_y = start_y
        
        for line in lines:
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            
            # 각 줄의 x 좌표 계산 (중앙 정렬)
            line_x = (img_width - line_width) // 2
            
            draw.text((line_x, current_y), line, font=font, fill=fill)
            current_y += line_height * 1.5 # 다음 줄로 이동

    def _draw_rounded_rectangle(self, draw, coords, radius, fill):
        """둥근 모서리 사각형 그리기"""
        x1, y1, x2, y2 = coords
        diameter = radius * 2
        
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        
        draw.ellipse([x1, y1, x1 + diameter, y1 + diameter], fill=fill)
        draw.ellipse([x2 - diameter, y1, x2, y1 + diameter], fill=fill)
        draw.ellipse([x1, y2 - diameter, x1 + diameter, y2], fill=fill)
        draw.ellipse([x2 - diameter, y2 - diameter, x2, y2], fill=fill)
    
    def _get_optimal_font_size(self, text, max_width, max_height, font_path=None, initial_size=60):
        font_size = initial_size
        
        while font_size > 10:  # 최소 폰트 크기는 10
            try:
                if font_path:
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    font = ImageFont.load_default()
                    return font
                    
                # 마침표를 기준으로 문장을 나누기
                sentences = text.split('.')
                wrapped_lines = []
                
                # 각 문장 처리
                for i, sentence in enumerate(sentences):
                    if sentence.strip():  # 빈 문장 제외
                        # 현재 문장을 줄바꿈 처리
                        char_limit = int(max_width / (font_size * 0.8))  # 폰트 크기를 고려한 글자 수 계산
                        wrapped = textwrap.fill(sentence.strip(), width=char_limit)
                        current_lines = wrapped.split('\n')
                        
                        # 마지막 줄에만 마침표 추가 (마지막 문장이 아닌 경우에만)
                        if i < len(sentences) - 1:
                            current_lines[-1] = current_lines[-1] + '.'
                        
                        wrapped_lines.extend(current_lines)
                
                wrapped_text = '\n'.join(wrapped_lines)
                lines = wrapped_text.split('\n')
                
                # 모든 줄의 최대 너비와 총 높이 계산
                max_line_width = 0
                total_height = 0
                line_spacing = font_size * 0.3
                
                for line in lines:
                    bbox = font.getbbox(line)
                    line_width = bbox[2] - bbox[0]
                    line_height = bbox[3] - bbox[1]
                    max_line_width = max(max_line_width, line_width)
                    total_height += line_height
                
                if len(lines) > 1:
                    total_height += line_spacing * (len(lines) - 1)
                
                if max_line_width <= max_width and total_height <= max_height:
                    return font, wrapped_text
                
            except Exception as e:
                self.logger.error(f"폰트 크기 조정 중 오류 발생: {e}")
                if font_size == initial_size:
                    font = ImageFont.load_default()
                    return font, text
                
            font_size -= 2
        
        font = ImageFont.load_default()
        return font, text

    def _draw_content_box(self, draw, text, font, width, start_y, text_color, box_color):
        """텍스트 배경 박스를 그리고 텍스트를 작성하는 메서드"""
        # 텍스트의 크기 계산
        lines = text.split('\n')
        total_height = 0
        max_width = 0
        line_spacing = font.size * 0.3
        
        # 첫 번째 라인의 실제 높이 계산 (ascent + descent)
        first_line = lines[0]
        ascent, descent = font.getmetrics()
        line_height = ascent + descent
        
        for line in lines:
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            max_width = max(max_width, line_width)
            total_height += line_height  # 실제 라인 높이 사용
        
        if len(lines) > 1:
            total_height += line_spacing * (len(lines) - 1)
        
        # 배경 박스의 패딩 설정
        padding_x = 40
        padding_y = 30
        
        # 텍스트의 실제 시작 위치 계산 (베이스라인 조정)
        text_start_y = start_y - (ascent * 0.1)  # 텍스트 위치를 약간 위로 조정
        
        # 배경 박스 좌표 계산
        box_left = (width - max_width) // 2 - padding_x
        box_top = text_start_y - padding_y
        box_right = (width + max_width) // 2 + padding_x
        box_bottom = text_start_y + total_height + padding_y
        
        # 배경 박스 그리기
        self._draw_rounded_rectangle(
            draw,
            [box_left, box_top, box_right, box_bottom],
            radius=20,
            fill=box_color
        )
        
        # 텍스트 그리기
        self._draw_multiline_text(
            draw, 
            text, 
            font, 
            width, 
            start_y=text_start_y, 
            fill=text_color
        )

    def create_card(self, no, term, short_description, description, output_path):
        """카드 이미지 생성"""

        sb_aggro_m_font_path = os.path.join('fonts', 'SB-Aggro-Medium.ttf')
        sb_aggro_b_font_path = os.path.join('fonts', 'SB-Aggro-Bold.ttf')
        gm_sans_b_font_path = os.path.join('fonts', 'GmarketSansTTFBold.ttf')

        try:
            img = Image.open(self.background_path)
        except FileNotFoundError:
            self.logger.error("배경 이미지를 찾을 수 없습니다.")
            return
        
        draw = ImageDraw.Draw(img)
        width, height = img.size

        # 타이틀 폰트 및 텍스트 설정
        term_font, term_text = self._get_optimal_font_size(term, 750, 200, sb_aggro_b_font_path, 165)
        self._draw_text(
            draw, 
            term_text, 
            term_font, 
            width, 
            start_y=260, 
            fill=(174, 151, 116)
        )

        # 짧은 설명 폰트 설정
        short_description_font, short_description_text = self._get_optimal_font_size(short_description, 780, 100, sb_aggro_m_font_path, 38)
        self._draw_multiline_text(
            draw, 
            short_description_text, 
            short_description_font, 
            width, 
            start_y=480, 
            fill=(180, 159, 126)
        )

        # 긴 설명 폰트 설정
        description_font, description_text = self._get_optimal_font_size(description, 700, 200, gm_sans_b_font_path, 36)
        self._draw_content_box(
            draw=draw,
            text=description_text,
            font=description_font,
            width=width,
            start_y=630,
            text_color=(255, 255, 255),
            box_color=(174, 151, 116)
        )
        
        # 서브 타이틀 작성 (고정 위치)
        subtitle_text = f"경제용어 {no}"
        draw.text((358, 130), subtitle_text, font=ImageFont.truetype(sb_aggro_m_font_path, 40), fill=(255, 255, 255))

        unique_output_path = self._get_unique_filename(output_path)
        img.save(unique_output_path)

def main():
    logger = LoggerUtil().get_logger()
    no = 1
    term = '매매'
    short_description = '값을 지불하고 재화나 용역을 사고 파는 것'
    description = '우리가 사용하는 당근 어플에서 중고 거래를 하는 것도 매매의 일종이에요.'

    logger.info(f'term: {term}')
    logger.info(f'short_description: {short_description}')
    logger.info(f'description: {description}')

    processor = ImageProcessor()
    processor.create_card(
        no=no,
        term=term,
        short_description=short_description,
        description=description,
        output_path="output.png"
    )

if __name__ == "__main__":
    main()