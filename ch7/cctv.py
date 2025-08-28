import zipfile
import os
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap, QKeyEvent, QImage
from PyQt5.QtCore import Qt


class MarsImageHelper:
    def __init__(self, folder_path="cctv"):
        self.folder_path = folder_path
        self.images = []
        self.current_index = 0
        self.search_index = 0
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.upperbody_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')

    def extract_zip(self, zip_path="cctv.zip"):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.folder_path)
        
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
    
    def next_image(self):
        if len(self.images) > 0:
            self.current_index = (self.current_index + 1) % len(self.images)
            return self.get_current_image_path()
        return None
    
    def prev_image(self):
        if len(self.images) > 0:
            self.current_index = (self.current_index - 1) % len(self.images)
            return self.get_current_image_path()
        return None
    
    def detect_person(self, image_path):
        if not image_path or not os.path.exists(image_path):
            return False, []
        
        img = cv2.imread(image_path)
        if img is None:
            return False, []
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        all_detections = []
        
        try:
            (rects, _) = self.hog.detectMultiScale(
                img, 
                winStride=(8, 8),
                padding=(32, 32), 
                scale=1.05
            )
            for rect in rects:
                all_detections.append({
                    'rect': (rect[0], rect[1], rect[2], rect[3]),
                    'type': 'HOG',
                    'color': (255, 0, 0)  # 빨간색
                })
        except:
            pass
            
        try:
            rects = self.upperbody_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(30, 30)
            )
            for rect in rects:
                all_detections.append({
                    'rect': rect,
                    'type': 'UpperBody',
                    'color': (0, 0, 255)  # 파란색
                })
        except:
            pass
        
        if len(all_detections) > 0:
            return True, all_detections
        return False, []
    
    def _create_person_template(self, width, height):
        template = np.zeros((height, width), dtype=np.uint8)
        
        # 머리 (타원)
        head_center = (width//2, height//6)
        head_axes = (width//4, height//8)
        cv2.ellipse(template, head_center, head_axes, 0, 0, 360, 255, -1)
        
        # 몸통 (사각형)
        body_top = height//4
        body_bottom = int(height * 0.7)
        body_left = width//3
        body_right = int(width * 0.67)
        cv2.rectangle(template, (body_left, body_top), (body_right, body_bottom), 255, -1)
        
        # 다리 (두 개의 사각형)
        leg_top = int(height * 0.65)
        leg_bottom = height - 1
        leg1_left = int(width * 0.3)
        leg1_right = int(width * 0.45)
        leg2_left = int(width * 0.55)
        leg2_right = int(width * 0.7)
        
        cv2.rectangle(template, (leg1_left, leg_top), (leg1_right, leg_bottom), 255, -1)
        cv2.rectangle(template, (leg2_left, leg_top), (leg2_right, leg_bottom), 255, -1)
        
        return template
    
    def _remove_overlapping_rects(self, rects, overlap_threshold=0.5):
        if len(rects) == 0:
            return []
            
        # 면적 기준으로 정렬 (큰 것부터)
        rects = sorted(rects, key=lambda x: x[2] * x[3], reverse=True)
        filtered = []
        
        for rect in rects:
            x1, y1, w1, h1 = rect
            is_duplicate = False
            
            for existing in filtered:
                x2, y2, w2, h2 = existing
                
                # 겹치는 영역 계산
                overlap_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                overlap_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
                overlap_area = overlap_x * overlap_y
                
                # 현재 사각형의 면적
                current_area = w1 * h1
                
                # 설정된 비율 이상 겹치면 중복으로 간주
                if overlap_area > overlap_threshold * current_area:
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                filtered.append(rect)
                
        return filtered
    
    def find_next_person_image(self):
        if len(self.images) == 0:
            return None, False
        
        if self.search_index < len(self.images):
            self.current_index = self.search_index
            image_path = self.get_current_image_path()
            has_person, detections = self.detect_person(image_path)
            
            return image_path, detections if has_person else []
        
        return None, False
    
    def continue_search(self):
        if self.search_index < len(self.images) - 1:
            self.search_index += 1
            return self.find_next_person_image()
        return None, False
    
    def reset_search(self):
        self.search_index = 0
    
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
        self.search_mode = False
        self.init_ui()
        self.display_current_image()
    
    def safe_close(self):
        try:
            self.close()
        except Exception as e:
            print(f"Close error: {e}")
            import sys
            sys.exit(0)
        
    def init_ui(self):
        self.setWindowTitle("CCTV Viewer")
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
        
        self.status_label = QLabel("Image Viewer Mode - Use ← → keys to navigate, S for person search, ESC to exit")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; color: blue; padding: 5px;")
        layout.addWidget(self.status_label)
        
    def display_current_image(self):
        if len(self.image_helper.images) == 0:
            self.image_label.setText("No images found in cctv folder")
            self.info_label.setText("Please check cctv.zip file")
            return
            
        image_path = self.image_helper.get_current_image_path()
        if image_path:
            self.display_image_simple(image_path)
    
    def display_image_simple(self, image_path):
        if not image_path or not os.path.exists(image_path):
            self.image_label.setText("No image to display")
            self.info_label.setText("No image loaded")
            return
        
        img = cv2.imread(image_path)
        height, width = img.shape[:2]
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        bytes_per_line = 3 * width
        q_image = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(q_image)
        
        max_width = 850
        max_height = 550
        if pixmap.width() > max_width or pixmap.height() > max_height:
            pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.image_label.setPixmap(pixmap)
        self.info_label.setText(self.image_helper.get_image_info())
    
    def start_search(self):
        self.search_mode = True
        self.search_completed = False

        self.image_helper.search_index = self.image_helper.current_index
        self.status_label.setText("Person Search Mode - Press Enter to navigate images...")
        self.status_label.setStyleSheet("font-size: 12px; color: blue; padding: 5px;")
        self.search_for_person()
    
    def exit_search_mode(self):
        self.search_mode = False
        self.search_completed = False
        self.current_detections = []
        self.status_label.setText("Image Viewer Mode - Use ← → keys to navigate, S for person search, ESC to exit")
        self.status_label.setStyleSheet("font-size: 12px; color: blue; padding: 5px;")
        self.display_current_image()
    
    def search_for_person(self):
        image_path, detections = self.image_helper.find_next_person_image()
        
        if image_path:
            self.current_detections = detections
            self.display_image_with_boxes(image_path)
            if len(detections) > 0:
                self.status_label.setText(f"Person detected! ({len(detections)} detection(s)) Press Enter to continue or V to exit.")
                self.status_label.setStyleSheet("font-size: 12px; color: green; padding: 5px;")
            else:
                self.status_label.setText("No person detected. Press Enter to continue or V to exit.")
                self.status_label.setStyleSheet("font-size: 12px; color: orange; padding: 5px;")
        else:
            self.search_completed = True
            self.status_label.setText("Search completed. Press V to exit search mode.")
            self.status_label.setStyleSheet("font-size: 12px; color: red; padding: 5px;")
            QMessageBox.information(self, "Search Complete", 
                                  "Search has been completed.\nNo more people found in the remaining images.")
    
    def display_image_with_boxes(self, image_path):
        if not image_path or not os.path.exists(image_path):
            self.image_label.setText("No image to display")
            self.info_label.setText("No image loaded")
            return
        
        img = cv2.imread(image_path)
        height, width = img.shape[:2]
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        for i, detection in enumerate(self.current_detections):
            x, y, w, h = detection['rect']
            color = detection['color']
            detection_type = detection['type']
            
            cv2.rectangle(img_rgb, (x, y), (x + w, y + h), color, 3)

            cv2.putText(img_rgb, detection_type, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
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
        try:
            if self.search_mode:
                if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                    if not self.search_completed:
                        image_path, detections = self.image_helper.continue_search()
                        if image_path:
                            self.current_detections = detections
                            self.display_image_with_boxes(image_path)
                            if len(detections) > 0:
                                self.status_label.setText(f"Person detected! ({len(detections)} detection(s)) Press Enter to continue or V to exit.")
                                self.status_label.setStyleSheet("font-size: 12px; color: green; padding: 5px;")
                            else:
                                self.status_label.setText("No person detected. Press Enter to continue or V to exit.")
                                self.status_label.setStyleSheet("font-size: 12px; color: orange; padding: 5px;")
                        else:
                            self.search_completed = True
                            self.status_label.setText("Search completed. Press V to exit search mode.")
                            self.status_label.setStyleSheet("font-size: 12px; color: red; padding: 5px;")
                elif event.key() == Qt.Key_V:
                    self.exit_search_mode()
            else:
                if event.key() == Qt.Key_Left:
                    prev_image = self.image_helper.prev_image()
                    if prev_image:
                        self.display_image_simple(prev_image)
                elif event.key() == Qt.Key_Right:
                    next_image = self.image_helper.next_image()
                    if next_image:
                        self.display_image_simple(next_image)
                elif event.key() == Qt.Key_S:
                    self.start_search()
            
            if event.key() == Qt.Key_Escape:
                self.safe_close()
        except Exception as e:
            print(f"Key event error: {e}")


def main():
    app = QApplication(sys.argv)
    viewer = CCTVViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()