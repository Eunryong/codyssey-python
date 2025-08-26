import zipfile
import os
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap, QKeyEvent, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect


class MarsImageHelper:
    def __init__(self, folder_path="CCTV"):
        self.folder_path = folder_path
        self.images = []
        self.current_index = 0
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
    def extract_zip(self, zip_path="cctv.zip"):
        if not os.path.exists(self.folder_path):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")
        
    def load_images(self):
        if os.path.exists(self.folder_path):
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
            self.images = []
            for f in os.listdir(self.folder_path):
                if f.lower().endswith(valid_extensions):
                    full_path = os.path.join(self.folder_path, f)
                    if os.path.isfile(full_path):
                        try:
                            test_img = cv2.imread(full_path)
                            if test_img is not None:
                                self.images.append(f)
                        except:
                            pass
            self.images.sort()
            return len(self.images) > 0
        return False
    
    def get_current_image_path(self):
        if 0 <= self.current_index < len(self.images):
            return os.path.join(self.folder_path, self.images[self.current_index])
        return None
    
    def detect_person(self, image_path):
        if not image_path or not os.path.exists(image_path):
            return False, []
        
        img = cv2.imread(image_path)
        if img is None:
            return False, []
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        (rects, weights) = self.hog.detectMultiScale(
            gray,
            winStride=(4, 4),
            padding=(8, 8),
            scale=1.05
        )
        
        if len(rects) > 0:
            return True, rects
        return False, []
    
    def find_next_person_image(self):
        if len(self.images) == 0:
            return None, False
        
        start_index = self.current_index
        
        while self.current_index < len(self.images):
            image_path = self.get_current_image_path()
            has_person, rects = self.detect_person(image_path)
            
            if has_person:
                return image_path, rects
            
            self.current_index += 1
        
        return None, False
    
    def continue_search(self):
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            return self.find_next_person_image()
        return None, False
    
    def reset_search(self):
        self.current_index = 0
    
    def get_image_info(self):
        if len(self.images) > 0:
            return f"Image {self.current_index + 1} of {len(self.images)}: {self.images[self.current_index]}"
        return "No images loaded"


class CCTVViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_helper = MarsImageHelper()
        self.image_helper.extract_zip()
        self.image_helper.load_images()
        self.current_detections = []
        self.search_completed = False
        self.init_ui()
        self.start_search()
        
    def init_ui(self):
        self.setWindowTitle("CCTV Person Detection Viewer")
        self.setGeometry(100, 100, 900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        self.image_label = QLabel()
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")
        layout.addWidget(self.image_label)
        
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.info_label)
        
        self.status_label = QLabel("Searching for people in images...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; color: blue; padding: 5px;")
        layout.addWidget(self.status_label)
        
    def start_search(self):
        self.search_completed = False
        self.image_helper.reset_search()
        self.search_for_person()
    
    def search_for_person(self):
        image_path, detections = self.image_helper.find_next_person_image()
        
        if image_path:
            self.current_detections = detections
            self.display_image_with_boxes(image_path)
            self.status_label.setText("Person found! Press Enter to continue searching.")
            self.status_label.setStyleSheet("font-size: 12px; color: green; padding: 5px;")
        else:
            self.search_completed = True
            self.status_label.setText("Search completed. No more people found.")
            self.status_label.setStyleSheet("font-size: 12px; color: red; padding: 5px;")
            QMessageBox.information(self, "Search Complete", 
                                  "Search has been completed.\nNo more people found in the remaining images.")
    
    def display_image_with_boxes(self, image_path):
        if not image_path or not os.path.exists(image_path):
            self.image_label.setText("No image to display")
            self.info_label.setText("No image loaded")
            return
        
        img = cv2.imread(image_path)
        height, width, channel = img.shape
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        for (x, y, w, h) in self.current_detections:
            cv2.rectangle(img_rgb, (x, y), (x + w, y + h), (255, 0, 0), 3)
        
        bytes_per_line = 3 * width
        q_image = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(q_image)
        
        max_width = 850
        max_height = 550
        if pixmap.width() > max_width or pixmap.height() > max_height:
            pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.image_label.setPixmap(pixmap)
        self.info_label.setText(f"{self.image_helper.get_image_info()} - {len(self.current_detections)} person(s) detected")
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if not self.search_completed:
                image_path, detections = self.image_helper.continue_search()
                if image_path:
                    self.current_detections = detections
                    self.display_image_with_boxes(image_path)
                    self.status_label.setText("Person found! Press Enter to continue searching.")
                    self.status_label.setStyleSheet("font-size: 12px; color: green; padding: 5px;")
                else:
                    self.search_completed = True
                    self.status_label.setText("Search completed. No more people found.")
                    self.status_label.setStyleSheet("font-size: 12px; color: red; padding: 5px;")
                    QMessageBox.information(self, "Search Complete", 
                                          "Search has been completed.\nNo more people found in the remaining images.")
        elif event.key() == Qt.Key_R:
            self.start_search()
        elif event.key() == Qt.Key_Escape:
            self.close()


def main():
    app = QApplication(sys.argv)
    viewer = CCTVViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()