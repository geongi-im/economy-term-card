import tkinter as tk
from PIL import Image, ImageTk
import os

class ImageCoordinateViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("이미지 좌표 확인")

        # 이미지 로드
        image_path = os.path.join('img', 'sub_01.png')
        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image)

        # 캔버스 생성
        self.canvas = tk.Canvas(root, width=self.image.width, height=self.image.height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)

        # 좌표 표시 레이블
        self.coord_label = tk.Label(root, text="좌표: (0, 0)")
        self.coord_label.pack()

        # 마우스 이벤트 바인딩
        self.canvas.bind('<Motion>', self.show_coordinates)
        self.canvas.bind('<Button-1>', self.on_click)

    def show_coordinates(self, event):
        x, y = event.x, event.y
        self.coord_label.config(text=f"좌표: ({x}, {y})")

    def on_click(self, event):
        x, y = event.x, event.y
        print(f"클릭한 좌표: ({x}, {y})")

def main():
    root = tk.Tk()
    app = ImageCoordinateViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 