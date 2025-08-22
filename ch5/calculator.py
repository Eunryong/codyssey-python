import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics

class Calculator:

    def __init__(self):
        self.values = []
        self.operators = []

    def push_value(self, value):
        self.values.append(value)

    def push_operator(self, operator):
        self.operators.append(operator)

    def change_operator(self, operator):
        if len(self.operators) == 0:
            return
        self.operators[-1] = operator

    def compare_value_operator(self):
        return len(self.values) != 0 and len(self.values) == len(self.operators)

    def reset(self):
        self.values.clear()
        self.operators.clear()
        return 0

    def equal(self):
        i = 0
        if self.compare_value_operator():
            self.operators.pop()

        while i < len(self.operators):
            if self.operators[i] in ['×', '÷']:
                if self.operators[i] == '×':
                    self.values[i] = self.multiply(self.values[i], self.values[i + 1])
                elif self.operators[i] == '÷':
                    self.values[i] = self.divide(self.values[i], self.values[i + 1])
                self.values.pop(i + 1)
                self.operators.pop(i)
            else:
                i += 1

        i = 0
        while i < len(self.operators):
            if self.operators[i] in ['+', '-']:
                if self.operators[i] == '+':
                    self.values[i] = self.add(self.values[i], self.values[i + 1])
                elif self.operators[i] == '-':
                    self.values[i] = self.subtract(self.values[i], self.values[i + 1])
                self.values.pop(i + 1)
                self.operators.pop(i)
            else:
                i += 1
        
        if len(self.operators) == 0:
            result = self.values[0]
            self.values.clear()
            return result

    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def subtract(a, b):
        return a - b

    @staticmethod
    def multiply(a, b):
        return a * b

    @staticmethod
    def divide(a, b):
        try:
            return a / b
        except ZeroDivisionError:
            print("Zero Division Error")

    @staticmethod
    def negative_positive(a):
        return a * -1
    
    @staticmethod
    def percent(a):
        return a / 100
    
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.input = ""
        self.current_input = "0"
        self.calculator = Calculator()
        self.base_font_size = 24  # 기본 폰트 크기
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('계산기')
        self.setGeometry(300, 300, 400, 550)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: white;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555;
                border-radius: 5px;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
            .operator {
                background-color: #ff9500;
            }
            .operator:hover {
                background-color: #ffad33;
            }
            QLineEdit {
                background-color: #1a1a1a;
                border: 2px solid #555;
                border-radius: 5px;
                font-weight: bold;
                padding: 20px;
                text-align: right;
            }
        """)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        
        # 디스플레이
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setText(self.current_input)
        self.display.setAlignment(Qt.AlignRight)
        # 초기 폰트 크기 설정
        self.adjust_font_size(self.current_input)
        main_layout.addWidget(self.display)
        
        # 버튼 그리드 레이아웃
        grid_layout = QGridLayout()
        
        # 버튼 정의
        buttons = [
            ('C', 0, 0, 1, 1), ('±', 0, 1, 1, 1), ('%', 0, 2, 1, 1), ('÷', 0, 3, 1, 1),
            ('7', 1, 0, 1, 1), ('8', 1, 1, 1, 1), ('9', 1, 2, 1, 1), ('×', 1, 3, 1, 1),
            ('4', 2, 0, 1, 1), ('5', 2, 1, 1, 1), ('6', 2, 2, 1, 1), ('-', 2, 3, 1, 1),
            ('1', 3, 0, 1, 1), ('2', 3, 1, 1, 1), ('3', 3, 2, 1, 1), ('+', 3, 3, 1, 1),
            ('0', 4, 0, 1, 2), ('.', 4, 2, 1, 1), ('=', 4, 3, 1, 1)
        ]
        
        # 버튼 생성 및 배치
        for text, row, col, rowspan, colspan in buttons:
            button = QPushButton(text)
            button.clicked.connect(lambda checked, t=text: self.button_clicked(t))
            
            # 연산자 버튼 스타일 적용
            if text in ['÷', '×', '-', '+', '=']:
                button.setProperty("class", "operator")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #ff9500;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: #ffad33;
                    }
                """)
            
            grid_layout.addWidget(button, row, col, rowspan, colspan)
        
        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)
        
    def format_number(self, number):
        """숫자를 소수점 6자리로 반올림하고 불필요한 0 제거"""
        if isinstance(number, float):
            # 소수점 6자리로 반올림
            rounded = round(number, 6)
            # 정수인 경우 정수로 반환
            if rounded == int(rounded):
                return str(int(rounded))
            else:
                # 소수점 이하 불필요한 0 제거
                return f"{rounded:.6f}".rstrip('0').rstrip('.')
        return str(number)
    
    def adjust_font_size(self, text):
        """텍스트 길이에 따라 폰트 크기 자동 조정"""
        display_width = self.display.width() - 30  # 패딩 고려
        
        # 다양한 폰트 크기 시도 (24부터 12까지)
        for font_size in range(self.base_font_size, 11, -1):
            font = QFont()
            font.setPointSize(font_size)
            font.setBold(True)
            
            font_metrics = QFontMetrics(font)
            text_width = font_metrics.horizontalAdvance(text)
            
            if text_width <= display_width or font_size == 12:
                self.display.setFont(font)
                break
    
    def update_display(self, text):
        """디스플레이 업데이트 및 폰트 크기 조정"""
        self.display.setText(text)
        self.adjust_font_size(text)
        
    def button_clicked(self, text):
        if text.isdigit() or text == '.':
            self.number_clicked(text)
        elif text in ['÷', '×', '-', '+']:
            self.operator_clicked(text)
        elif text == '=':
            self.equals_clicked()
        elif text == 'C':
            self.clear_clicked()
        elif text == '±':
            self.plus_minus_clicked()
        elif text == '%':
            self.percent_clicked()
        self.update_display(self.input)
    
    def number_clicked(self, number):
        if number == '.':
            if self.current_input == '':
                self.current_input = '0.'
                self.input += self.current_input
            else:
                self.input += '' if number in self.current_input else number
                self.current_input += '' if number in self.current_input else number
        else:
            if self.current_input == '0':
                self.current_input = number
            else:
                self.current_input += number
            
            if self.input == '0':
                self.input = number
            else:
                self.input += number
    
    def operator_clicked(self, op):
        if self.current_input:
            self.calculator.push_value(float(self.current_input))
            self.current_input = ''

        if self.calculator.compare_value_operator():
            self.calculator.change_operator(op)
            self.input = self.input[:-1] + op
        else:
            self.calculator.push_operator(op)
            self.input += op

    
    def equals_clicked(self):
        try:
            self.calculator.push_value(float(self.current_input))
            result = self.calculator.equal()
            
            # 결과를 포맷팅 (소수점 6자리 반올림)
            formatted_result = self.format_number(result)
            
            self.input = formatted_result
            self.current_input = formatted_result
        except ZeroDivisionError:
            self.update_display("오류")
            self.calculator.reset()
            self.clear()
        except:
            self.update_display("오류")
            self.calculator.reset()
            self.clear()
    
    def clear_clicked(self):
        self.clear()
    
    def clear(self):
        self.calculator.reset()
        self.current_input = '0'
        self.input = "0"
        self.update_display(self.current_input)

    
    def plus_minus_clicked(self):
        if self.current_input and self.current_input != "0":
            value = float(self.current_input)
            result = self.calculator.negative_positive(value)
            
            # 결과를 포맷팅
            formatted_result = self.format_number(result)
            
            original_length = len(self.current_input)
            self.current_input = formatted_result
            self.input = self.input[:-original_length] + self.current_input
    
    def percent_clicked(self):
        if self.current_input == '':
            return
        value = float(self.current_input)
        original_length = len(self.current_input)

        result = self.calculator.percent(value)
        
        # 결과를 포맷팅
        formatted_result = self.format_number(result)
        
        self.current_input = formatted_result
        self.input = self.input[:-original_length] + self.current_input
        

def main():
    app = QApplication(sys.argv)
    calculator = App()
    calculator.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()