import sys

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QPushButton, QLineEdit, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics


class Calculator:

    def __init__(self):
        self.expression = ""

    def reset(self):
        self.expression = ""
        return 0

    def evaluate(self, expr):
        """수식을 eval로 계산"""
        try:
            # 연산자 기호 변환
            expr = expr.replace('×', '*').replace('÷', '/')
            
            # 마지막 문자가 연산자면 제거
            if expr and expr[-1] in '+-*/':
                expr = expr[:-1]
            
            # 빈 문자열이면 0 반환
            if not expr:
                return 0
                
            result = eval(expr)
            return result
        except ZeroDivisionError:
            raise ZeroDivisionError("Zero Division Error")
        except Exception:
            return 0

    @staticmethod
    def negative_positive(a):
        return a * -1
    
    @staticmethod
    def percent(a):
        return a / 100


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.expression = "0"  # 현재 수식
        self.current_input = ""  # 현재 입력 중인 숫자
        self.calculator = Calculator()
        self.base_font_size = 24  # 기본 폰트 크기
        self.just_evaluated = False  # = 버튼을 방금 눌렀는지 확인
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
        self.display.setText(self.expression)
        self.display.setAlignment(Qt.AlignRight)
        # 초기 폰트 크기 설정
        self.adjust_font_size(self.expression)
        main_layout.addWidget(self.display)
        
        # 버튼 그리드 레이아웃
        grid_layout = QGridLayout()
        
        # 버튼 정의
        buttons = [
            ('C', 0, 0, 1, 1), ('±', 0, 1, 1, 1),
            ('%', 0, 2, 1, 1), ('÷', 0, 3, 1, 1),
            ('7', 1, 0, 1, 1), ('8', 1, 1, 1, 1),
            ('9', 1, 2, 1, 1), ('×', 1, 3, 1, 1),
            ('4', 2, 0, 1, 1), ('5', 2, 1, 1, 1),
            ('6', 2, 2, 1, 1), ('-', 2, 3, 1, 1),
            ('1', 3, 0, 1, 1), ('2', 3, 1, 1, 1),
            ('3', 3, 2, 1, 1), ('+', 3, 3, 1, 1),
            ('0', 4, 0, 1, 2), ('.', 4, 2, 1, 1),
            ('=', 4, 3, 1, 1)
        ]
        
        # 버튼 생성 및 배치
        for text, row, col, rowspan, colspan in buttons:
            button = QPushButton(text)
            button.clicked.connect(
                lambda checked, t=text: self.button_clicked(t))
            
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
        self.update_display(self.expression)
    
    def number_clicked(self, number):
        # = 버튼 직후 새 숫자 입력시 초기화
        if self.just_evaluated:
            self.expression = ""
            self.current_input = ""
            self.just_evaluated = False
        
        if number == '.':
            if self.current_input == '':
                self.current_input = '0.'
                if self.expression == "0" or self.expression == "":
                    self.expression = "0."
                else:
                    self.expression += '0.'
            elif '.' not in self.current_input:
                self.current_input += number
                self.expression += number
        else:
            if self.expression == "0":
                self.expression = number
                self.current_input = number
            elif self.current_input == "0":
                # 현재 입력이 0이면 교체
                self.current_input = number
                # expression에서 마지막 0을 교체
                expr_len = len(self.expression)
                if expr_len > 0 and self.expression[-1] == '0':
                    self.expression = self.expression[:-1] + number
                else:
                    self.expression += number
            else:
                self.current_input += number
                self.expression += number
    
    def operator_clicked(self, op):
        # = 버튼 직후 연산자 입력시 결과를 기반으로 계속
        if self.just_evaluated:
            self.just_evaluated = False
        
        # 표현식이 비어있거나 0이면 0을 기반으로 시작
        if self.expression == "" or self.expression == "0":
            self.expression = "0" + op
        # 이미 연산자로 끝나면 교체
        elif self.expression[-1] in '÷×-+':
            self.expression = self.expression[:-1] + op
        else:
            self.expression += op
        
        self.current_input = ''

    
    def equals_clicked(self):
        try:
            # 빈 표현식이면 현재 입력값 사용
            if not self.expression and self.current_input:
                self.expression = self.current_input
            
            # 연산자로 끝나면 제거
            if self.expression and self.expression[-1] in "÷×-+":
                self.expression = self.expression[:-1]
            
            # 표현식 평가
            if self.expression and self.expression != "":
                result = self.calculator.evaluate(self.expression)
                formatted_result = self.format_number(result)
                self.expression = formatted_result
                self.current_input = formatted_result
                self.just_evaluated = True
        except ZeroDivisionError:
            self.update_display("오류")
            self.clear()
        except Exception as e:
            self.update_display("오류")
            self.clear()
    
    def clear_clicked(self):
        self.clear()
    
    def clear(self):
        self.calculator.reset()
        self.current_input = ''
        self.expression = "0"
        self.just_evaluated = False
        self.update_display(self.expression)

    
    def plus_minus_clicked(self):
        if self.current_input and self.current_input != "0":
            if self.current_input.startswith('-'):
                self.current_input = self.current_input[1:]
                # 표현식에서도 - 제거
                if self.expression.startswith('(-'):
                    end_paren = self.expression.endswith(')')
                    self.expression = (self.expression[2:-1]
                                       if end_paren
                                       else self.expression[1:])
            else:
                self.current_input = '-' + self.current_input
                # 표현식에 - 추가
                self.expression = '(-' + self.expression + ')'
    
    def percent_clicked(self):
        if self.just_evaluated:
            self.just_evaluated = False
            
        if self.expression and self.expression[-1] not in "+×÷-(":
            self.expression = "(" + self.expression + ")/100"
            self.current_input = ''
        

def main():
    app = QApplication(sys.argv)
    calculator = App()
    calculator.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()