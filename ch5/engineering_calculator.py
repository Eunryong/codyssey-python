import sys
import math
import random

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QPushButton, QLineEdit, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics

from calculator import Calculator


class EngineeringCalculator(Calculator):

    def __init__(self):
        super().__init__()
        self.memory = 0
        self.angle_mode = 'deg'  # deg or rad
        self.second_mode = False  # for 2nd function key
        self.random_used = False  # Track if random has been used
        
    @staticmethod
    def factorial(n):
        if n < 0:
            raise ValueError(
                "Factorial is not defined for negative numbers")
        if n == 0 or n == 1:
            return 1
        result = 1
        for i in range(2, int(n) + 1):
            result *= i
        return result
    
    @staticmethod
    def sin(x, mode='deg'):
        if mode == 'deg':
            x = math.radians(x)
        return math.sin(x)
    
    @staticmethod
    def cos(x, mode='deg'):
        if mode == 'deg':
            x = math.radians(x)
        return math.cos(x)
    
    @staticmethod
    def tan(x, mode='deg'):
        if mode == 'deg':
            x = math.radians(x)
        return math.tan(x)
    
    @staticmethod
    def sinh(x):
        return math.sinh(x)
    
    @staticmethod
    def cosh(x):
        return math.cosh(x)
    
    @staticmethod
    def tanh(x):
        return math.tanh(x)
    
    @staticmethod
    def asin(x, mode='deg'):
        result = math.asin(x)
        if mode == 'deg':
            result = math.degrees(result)
        return result
    
    @staticmethod
    def acos(x, mode='deg'):
        result = math.acos(x)
        if mode == 'deg':
            result = math.degrees(result)
        return result
    
    @staticmethod
    def atan(x, mode='deg'):
        result = math.atan(x)
        if mode == 'deg':
            result = math.degrees(result)
        return result
    
    @staticmethod
    def asinh(x):
        return math.asinh(x)
    
    @staticmethod
    def acosh(x):
        return math.acosh(x)
    
    @staticmethod
    def atanh(x):
        return math.atanh(x)
    
    @staticmethod
    def log(x):
        return math.log10(x)
    
    @staticmethod
    def ln(x):
        return math.log(x)
    
    @staticmethod
    def power(x, y):
        return x ** y
    
    @staticmethod
    def square(x):
        return x ** 2
    
    @staticmethod
    def cube(x):
        return x ** 3
    
    @staticmethod
    def sqrt(x):
        return math.sqrt(x)
    
    @staticmethod
    def cbrt(x):
        return x ** (1/3)
    
    @staticmethod
    def nth_root(x, n):
        return x ** (1/n)
    
    @staticmethod
    def reciprocal(x):
        if x == 0:
            raise ValueError("Division by zero")
        return 1 / x
    
    @staticmethod
    def exp(x):
        return math.exp(x)
    
    @staticmethod
    def ten_power(x):
        return 10 ** x
    
    @staticmethod
    def two_power(x):
        return 2 ** x
    
    @staticmethod
    def pi():
        return math.pi
    
    @staticmethod
    def e():
        return math.e
    
    def random(self):
        if self.random_used:
            raise ValueError("Random function can only be used once")
        self.random_used = True
        return random.random()
    
    def memory_clear(self):
        self.memory = 0
    
    def memory_add(self, value):
        self.memory += value
    
    def memory_subtract(self, value):
        self.memory -= value
    
    def memory_recall(self):
        return self.memory


class EngineeringApp(QWidget):
    def __init__(self):
        super().__init__()
        self.input = ""
        self.current_input = ""
        self.calculator = EngineeringCalculator()
        self.base_font_size = 20
        self.last_result = None
        self.expression = "0"  # 수식 표시용
        self.pending_function = None  # 대기 중인 함수
        self.just_evaluated = False  # = 버튼을 방금 눌렀는지 확인
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('공학용 계산기')
        self.setGeometry(100, 100, 900, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #1c1c1e;
                color: white;
            }
            QPushButton {
                background-color: #2c2c2e;
                border: 0.5px solid #3c3c3e;
                border-radius: 0px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px;
                color: white;
            }
            QPushButton:hover {
                background-color: #3c3c3e;
            }
            QPushButton:pressed {
                background-color: #4c4c4e;
            }
            .number {
                background-color: #505050;
                font-size: 16px;
            }
            .number:hover {
                background-color: #606060;
            }
            .operator {
                background-color: #ff9500;
            }
            .operator:hover {
                background-color: #ffad33;
            }
            .function {
                background-color: #2c2c2e;
                font-size: 13px;
            }
            .function:hover {
                background-color: #3c3c3e;
            }
            .memory {
                background-color: #2c2c2e;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #1c1c1e;
                border: none;
                border-radius: 0px;
                font-weight: 300;
                padding: 15px;
                text-align: right;
                font-size: 32px;
            }
        """)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 디스플레이
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setText("0")
        self.display.setAlignment(Qt.AlignRight)
        self.display.setMinimumHeight(80)
        main_layout.addWidget(self.display)
        
        # 버튼 그리드 레이아웃
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # 아이폰 공학용 계산기 버튼 배치
        buttons = [
            # Row 0
            ('(', 0, 0, 'function'), (')', 0, 1, 'function'),
            ('mc', 0, 2, 'memory'), ('m+', 0, 3, 'memory'),
            ('m-', 0, 4, 'memory'), ('mr', 0, 5, 'memory'),
            ('C', 0, 6, 'function'), ('±', 0, 7, 'function'),
            ('%', 0, 8, 'function'), ('÷', 0, 9, 'operator'),
            
            # Row 1
            ('2nd', 1, 0, 'function'), ('x²', 1, 1, 'function'),
            ('x³', 1, 2, 'function'), ('xʸ', 1, 3, 'function'),
            ('eˣ', 1, 4, 'function'), ('10ˣ', 1, 5, 'function'),
            ('7', 1, 6, 'number'), ('8', 1, 7, 'number'),
            ('9', 1, 8, 'number'), ('×', 1, 9, 'operator'),
            
            # Row 2
            ('¹/ₓ', 2, 0, 'function'), ('²√x', 2, 1, 'function'),
            ('³√x', 2, 2, 'function'), ('ʸ√x', 2, 3, 'function'),
            ('ln', 2, 4, 'function'), ('log₁₀', 2, 5, 'function'),
            ('4', 2, 6, 'number'), ('5', 2, 7, 'number'),
            ('6', 2, 8, 'number'), ('-', 2, 9, 'operator'),
            
            # Row 3
            ('x!', 3, 0, 'function'), ('sin', 3, 1, 'function'),
            ('cos', 3, 2, 'function'), ('tan', 3, 3, 'function'),
            ('e', 3, 4, 'function'), ('EE', 3, 5, 'function'),
            ('1', 3, 6, 'number'), ('2', 3, 7, 'number'),
            ('3', 3, 8, 'number'), ('+', 3, 9, 'operator'),
            
            # Row 4
            ('Rad', 4, 0, 'function'), ('sinh', 4, 1, 'function'),
            ('cosh', 4, 2, 'function'), ('tanh', 4, 3, 'function'),
            ('π', 4, 4, 'function'), ('Rand', 4, 5, 'function'),
            ('0', 4, 6, 'number', 2), ('', 4, 7, 'hidden'),
            ('.', 4, 8, 'number'), ('=', 4, 9, 'operator')
        ]
        
        # 버튼 생성 및 배치
        for button_info in buttons:
            if len(button_info) == 4:
                text, row, col, style = button_info
                colspan = 1
            elif len(button_info) == 5:
                text, row, col, style, colspan = button_info
            
            if style == 'hidden':
                continue
                
            button = QPushButton(text)
            button.clicked.connect(
                lambda checked, t=text: self.button_clicked(t))
            
            # 스타일 적용
            if style == 'number':
                button.setProperty("class", "number")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #505050;
                        color: white;
                        font-size: 18px;
                    }
                    QPushButton:hover {
                        background-color: #606060;
                    }
                """)
            elif style == 'operator':
                button.setProperty("class", "operator")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #ff9500;
                        color: white;
                        font-size: 18px;
                    }
                    QPushButton:hover {
                        background-color: #ffad33;
                    }
                """)
            elif style == 'function':
                button.setProperty("class", "function")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2c2c2e;
                        color: white;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #3c3c3e;
                    }
                """)
            elif style == 'memory':
                button.setProperty("class", "memory")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2c2c2e;
                        color: #808080;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #3c3c3e;
                    }
                """)
            
            button.setMinimumHeight(50)
            grid_layout.addWidget(button, row, col, 1, colspan)
        
        # 2nd 버튼 참조 저장
        self.second_button = None
        self.rad_button = None
        for i in range(grid_layout.count()):
            widget = grid_layout.itemAt(i).widget()
            if widget and widget.text() == '2nd':
                self.second_button = widget
            elif widget and widget.text() == 'Rad':
                self.rad_button = widget
        
        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)
        
    def format_number(self, number):
        """숫자를 소수점 10자리로 반올림하고 불필요한 0 제거"""
        if isinstance(number, float):
            # 소수점 10자리로 반올림
            rounded = round(number, 10)
            # 정수인 경우 정수로 반환
            if rounded == int(rounded):
                return str(int(rounded))
            else:
                # 소수점 이하 불필요한 0 제거
                formatted = f"{rounded:.10f}".rstrip('0').rstrip('.')
                # 과학적 표기법 처리
                if abs(rounded) < 1e-10 or abs(rounded) > 1e10:
                    return f"{rounded:.6e}"
                return formatted
        return str(number)
    
    def evaluate_expression(self, expr):
        """수식 문자열을 평가하여 결과 반환"""
        import re
        
        # 수식 정리
        expr = expr.replace('×', '*').replace('÷', '/').replace('^', '**')
        
        # π와 e를 임시 마커로 치환
        expr = expr.replace('π', '__PI__')
        expr = expr.replace('e', '__E__')
        
        # 과학적 표기법 처리 (E를 e로)
        expr = expr.replace('E', 'e')
        
        # 마커를 실제 값으로 치환
        expr = expr.replace('__PI__', str(math.pi))
        expr = expr.replace('__E__', str(math.e))
        
        expr = expr.replace('²', '**2').replace('³', '**3')
        
        # 함수 매핑 - 삼각함수
        expr = re.sub(
            r'sin\((.*?)\)',
            lambda m: str(self.calculator.sin(
                float(self.evaluate_expression(m.group(1))),
                self.calculator.angle_mode)), expr)
        expr = re.sub(
            r'cos\((.*?)\)',
            lambda m: str(self.calculator.cos(
                float(self.evaluate_expression(m.group(1))),
                self.calculator.angle_mode)), expr)
        expr = re.sub(
            r'tan\((.*?)\)',
            lambda m: str(self.calculator.tan(
                float(self.evaluate_expression(m.group(1))),
                self.calculator.angle_mode)), expr)
        
        # 쌍곡선 함수
        expr = re.sub(
            r'sinh\((.*?)\)',
            lambda m: str(self.calculator.sinh(
                float(self.evaluate_expression(m.group(1))))), expr)
        expr = re.sub(
            r'cosh\((.*?)\)',
            lambda m: str(self.calculator.cosh(
                float(self.evaluate_expression(m.group(1))))), expr)
        expr = re.sub(
            r'tanh\((.*?)\)',
            lambda m: str(self.calculator.tanh(
                float(self.evaluate_expression(m.group(1))))), expr)
        
        # 역삼각 함수
        expr = re.sub(
            r'asin\((.*?)\)',
            lambda m: str(self.calculator.asin(
                float(self.evaluate_expression(m.group(1))),
                self.calculator.angle_mode)), expr)
        expr = re.sub(
            r'acos\((.*?)\)',
            lambda m: str(self.calculator.acos(
                float(self.evaluate_expression(m.group(1))),
                self.calculator.angle_mode)), expr)
        expr = re.sub(
            r'atan\((.*?)\)',
            lambda m: str(self.calculator.atan(
                float(self.evaluate_expression(m.group(1))),
                self.calculator.angle_mode)), expr)
        
        # 역쌍곡선 함수
        expr = re.sub(
            r'asinh\((.*?)\)',
            lambda m: str(self.calculator.asinh(
                float(self.evaluate_expression(m.group(1))))), expr)
        expr = re.sub(
            r'acosh\((.*?)\)',
            lambda m: str(self.calculator.acosh(
                float(self.evaluate_expression(m.group(1))))), expr)
        expr = re.sub(
            r'atanh\((.*?)\)',
            lambda m: str(self.calculator.atanh(
                float(self.evaluate_expression(m.group(1))))), expr)
        
        # 로그 함수
        expr = re.sub(
            r'ln\((.*?)\)',
            lambda m: str(self.calculator.ln(
                float(self.evaluate_expression(m.group(1))))), expr)
        expr = re.sub(
            r'log\((.*?)\)',
            lambda m: str(self.calculator.log(
                float(self.evaluate_expression(m.group(1))))), expr)
        
        # 제곱근 함수
        expr = re.sub(
            r'√\((.*?)\)',
            lambda m: str(self.calculator.sqrt(
                float(self.evaluate_expression(m.group(1))))), expr)
        expr = re.sub(
            r'³√\((.*?)\)',
            lambda m: str(self.calculator.cbrt(
                float(self.evaluate_expression(m.group(1))))), expr)
        
        # 팩토리얼 처리
        expr = re.sub(
            r'\((.*?)\)!',
            lambda m: str(self.calculator.factorial(
                float(self.evaluate_expression(m.group(1))))), expr)
        expr = re.sub(
            r'(\d+)!',
            lambda m: str(self.calculator.factorial(
                float(m.group(1)))), expr)
        
        # n제곱근 처리 (예: 4√16)
        expr = re.sub(
            r'(\d+)√(\d+)',
            lambda m: str(self.calculator.nth_root(
                float(m.group(2)), float(m.group(1)))), expr)
        
        # Python eval로 계산
        try:
            result = eval(expr)
            return result
        except:
            # eval 실패시 원본 반환
            is_number = expr.replace('.', '').replace('-', '').isdigit()
            return float(expr) if is_number else 0
    
    def adjust_font_size(self, text):
        """텍스트 길이에 따라 폰트 크기 자동 조정"""
        display_width = self.display.width() - 30
        
        for font_size in range(32, 11, -2):
            font = QFont()
            font.setPointSize(font_size)
            font.setWeight(QFont.Light)
            
            font_metrics = QFontMetrics(font)
            text_width = font_metrics.horizontalAdvance(text)
            
            if text_width <= display_width or font_size == 12:
                self.display.setFont(font)
                break
    
    def update_display(self, text=None):
        """디스플레이 업데이트 및 폰트 크기 조정"""
        if text is None:
            text = self.expression if self.expression else self.current_input
        self.display.setText(text)
        self.adjust_font_size(text)
        
    def button_clicked(self, text):
        try:
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
            elif text == '(':
                self.left_paren_clicked()
            elif text == ')':
                self.right_paren_clicked()
            elif text == '2nd':
                self.second_clicked()
            elif text == 'Rad':
                self.toggle_angle_mode()
            elif text in ['sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh']:
                self.trig_clicked(text)
            elif text == 'x²':
                self.square_clicked()
            elif text == 'x³':
                self.cube_clicked()
            elif text == 'xʸ':
                self.power_clicked()
            elif text == '²√x':
                self.sqrt_clicked()
            elif text == '³√x':
                self.cbrt_clicked()
            elif text == 'ʸ√x':
                self.nth_root_clicked()
            elif text == '¹/ₓ':
                self.reciprocal_clicked()
            elif text == 'ln':
                self.ln_clicked()
            elif text == 'log₁₀':
                self.log_clicked()
            elif text == 'eˣ':
                self.exp_clicked()
            elif text == '10ˣ':
                self.ten_power_clicked()
            elif text == 'x!':
                self.factorial_clicked()
            elif text == 'π':
                self.pi_clicked()
            elif text == 'e':
                self.e_clicked()
            elif text == 'Rand':
                self.rand_clicked()
            elif text == 'EE':
                self.ee_clicked()
            elif text == 'mc':
                self.memory_clear_clicked()
            elif text == 'm+':
                self.memory_add_clicked()
            elif text == 'm-':
                self.memory_subtract_clicked()
            elif text == 'mr':
                self.memory_recall_clicked()
                
            self.update_display()
        except Exception as e:
            self.update_display("Error")
            print(f"Error: {e}")
    
    def number_clicked(self, number):
        # = 버튼 직후 새 숫자 입력시 초기화
        if self.just_evaluated:
            self.expression = ""
            self.current_input = ""
            self.just_evaluated = False
        
        # 함수가 대기 중이면 괄호만 열고 숫자는 입력하지 않음
        if self.pending_function:
            self.expression += self.pending_function + "("
            self.pending_function = None
            self.current_input = ""
            return  # 숫자 입력 차단
        
        # 괄호 ')' 다음에 숫자가 바로 입력되지 않도록 차단
        if (self.expression and 
            len(self.expression) > 0 and 
            self.expression[-1] == ')' and 
            (number.isdigit() or number == '.')):
            return  # 숫자 입력 차단
        
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
                if len(self.expression) > 0 and self.expression[-1] == '0':
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
        
        # 대기 중인 함수가 있으면 닫기
        if self.pending_function:
            if self.current_input:
                self.expression += (self.pending_function + "(" +
                                    self.current_input + ")")
            self.pending_function = None
        
        # 표현식이 비어있거나 0이면 0을 기반으로 시작
        if self.expression == "" or self.expression == "0":
            self.expression = "0" + op
        # 이미 연산자로 끝나면 교체
        elif self.expression[-1] in "+-×÷^":
            self.expression = self.expression[:-1] + op
        else:
            self.expression += op
        
        self.current_input = ''
    
    def equals_clicked(self):
        try:
            # 대기 중인 함수 처리
            if self.pending_function and self.current_input:
                self.expression = (self.pending_function + "(" +
                                   self.current_input + ")")
                self.pending_function = None
            elif self.pending_function:
                # 입력값이 없으면 현재 표현식 사용
                self.expression = (self.pending_function + "(" +
                                   self.expression + ")")
                self.pending_function = None
            
            # 빈 표현식이면 현재 입력값 사용
            if not self.expression and self.current_input:
                self.expression = self.current_input
            
            # 연산자로 끝나면 제거
            if self.expression and self.expression[-1] in "+-×÷^":
                self.expression = self.expression[:-1]
            
            # 표현식 평가
            if self.expression and self.expression != "":
                result = self.evaluate_expression(self.expression)
                formatted_result = self.format_number(result)
                self.expression = formatted_result
                self.current_input = formatted_result
                self.last_result = result
                self.just_evaluated = True
        except Exception as e:
            self.update_display("Error")
            self.clear()
            print(f"Evaluation error: {e}")
    
    def clear_clicked(self):
        self.clear()
    
    def clear(self):
        self.calculator.reset()
        self.current_input = ''
        self.expression = '0'
        self.pending_function = None
        self.just_evaluated = False
        self.update_display()
    
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
            
        if self.expression and self.expression[-1] not in "+-×÷^(":
            self.expression = "(" + self.expression + ")/100"
            self.current_input = ''
    
    def left_paren_clicked(self):
        if self.pending_function:
            self.expression += self.pending_function + "("
            self.pending_function = None
        else:
            self.expression += '('
        self.current_input = ''
    
    def right_paren_clicked(self):
        self.expression += ')'
        self.current_input = ''
    
    def second_clicked(self):
        self.calculator.second_mode = not self.calculator.second_mode
        if self.second_button:
            if self.calculator.second_mode:
                self.second_button.setStyleSheet("""
                    QPushButton {
                        background-color: #ff9500;
                        color: white;
                        font-size: 14px;
                    }
                """)
            else:
                self.second_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2c2c2e;
                        color: white;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #3c3c3e;
                    }
                """)
    
    def toggle_angle_mode(self):
        if self.calculator.angle_mode == 'deg':
            self.calculator.angle_mode = 'rad'
            if self.rad_button:
                self.rad_button.setText('Deg')
        else:
            self.calculator.angle_mode = 'deg'
            if self.rad_button:
                self.rad_button.setText('Rad')
    
    def trig_clicked(self, func):
        if self.just_evaluated:
            self.just_evaluated = False
            
        if self.calculator.second_mode:
            # 2nd 모드: 역삼각함수
            self.calculator.second_mode = False
            self.second_clicked()  # UI 업데이트
            
            if func == 'sin':
                func_name = 'asin'
            elif func == 'cos':
                func_name = 'acos'
            elif func == 'tan':
                func_name = 'atan'
            elif func == 'sinh':
                func_name = 'asinh'
            elif func == 'cosh':
                func_name = 'acosh'
            elif func == 'tanh':
                func_name = 'atanh'
        else:
            func_name = func
        
        # 현재 표현식이 있으면 함수 적용 (0 포함)
        if self.expression:
            # 연산자로 끝나면 대기
            if self.expression[-1] in "+-×÷^(":
                self.pending_function = func_name
            else:
                self.expression = func_name + "(" + self.expression + ")"
                self.current_input = ''
        else:
            # 입력값이 없으면 대기
            self.pending_function = func_name
    
    def square_clicked(self):
        if self.just_evaluated:
            self.just_evaluated = False
            
        if self.expression and self.expression[-1] not in "+-×÷^(":
            self.expression = "(" + self.expression + ")²"
            self.current_input = ''
    
    def cube_clicked(self):
        if self.just_evaluated:
            self.just_evaluated = False
            
        if self.expression and self.expression[-1] not in "+-×÷^(":
            self.expression = "(" + self.expression + ")³"
            self.current_input = ''
    
    def power_clicked(self):
        if self.just_evaluated:
            self.just_evaluated = False
            
        # 현재 표현식이 숫자나 유효한 값으로 끝나는 경우에만 처리
        if self.expression and self.expression[-1] not in "+-×÷^(":
            self.expression = "(" + self.expression + ")^"
            self.current_input = ''
    
    def sqrt_clicked(self):
        if self.just_evaluated:
            self.just_evaluated = False
            
        if self.expression and self.expression[-1] not in "+-×÷^(":
            self.expression = "√(" + self.expression + ")"
            self.current_input = ''
        else:
            self.pending_function = '√'
    
    def cbrt_clicked(self):
        if self.just_evaluated:
            self.just_evaluated = False
            
        if self.expression and self.expression[-1] not in "+-×÷^(":
            self.expression = "³√(" + self.expression + ")"
            self.current_input = ''
        else:
            self.pending_function = '³√'
    
    def nth_root_clicked(self):
        if self.current_input:
            self.expression += "√"
            self.current_input = ''
    
    def reciprocal_clicked(self):
        if self.just_evaluated:
            self.just_evaluated = False
            
        if self.expression and self.expression[-1] not in "+-×÷^(":
            self.expression = "1/(" + self.expression + ")"
            self.current_input = ''
    
    def ln_clicked(self):
        if self.just_evaluated:
            self.just_evaluated = False
            
        if self.expression and self.expression[-1] not in "+-×÷^(":
            self.expression = "ln(" + self.expression + ")"
            self.current_input = ''
        else:
            self.pending_function = 'ln'
    
    def log_clicked(self):
        if self.just_evaluated:
            self.just_evaluated = False
            
        if self.expression and self.expression[-1] not in "+-×÷^(":
            self.expression = "log(" + self.expression + ")"
            self.current_input = ''
        else:
            self.pending_function = 'log'
    
    def exp_clicked(self):
        if self.just_evaluated:
            self.just_evaluated = False
            
        if self.expression and self.expression[-1] not in "+-×÷^(":
            self.expression = "e^(" + self.expression + ")"
            self.current_input = ''
        else:
            self.expression += "e^"
    
    def ten_power_clicked(self):
        if self.just_evaluated:
            self.just_evaluated = False
            
        if self.expression and self.expression[-1] not in "+-×÷^(":
            self.expression = "10^(" + self.expression + ")"
            self.current_input = ''
        else:
            self.expression += "10^"
    
    def factorial_clicked(self):
        if self.just_evaluated:
            self.just_evaluated = False
            
        if self.expression and self.expression[-1] not in "+-×÷^(":
            self.expression = "(" + self.expression + ")!"
            self.current_input = ''
    
    def pi_clicked(self):
        if self.just_evaluated:
            self.expression = ""
            self.just_evaluated = False
            
        if self.pending_function:
            self.expression += self.pending_function + "(π)"
            self.pending_function = None
        elif self.expression == "0" or self.expression == "":
            self.expression = "π"
        elif self.expression[-1] in "+-×÷^(":
            # 연산자나 괄호 뒤에는 그대로 추가
            self.expression += "π"
        elif self.expression[-1] in "0123456789.πe)":
            # 숫자나 상수 뒤에는 곱셈 연산자 추가
            self.expression += "×π"
        else:
            self.expression += "π"
        self.current_input = ''
    
    def e_clicked(self):
        if self.just_evaluated:
            self.expression = ""
            self.just_evaluated = False
            
        if self.pending_function:
            self.expression += self.pending_function + "(e)"
            self.pending_function = None
        elif self.expression == "0" or self.expression == "":
            self.expression = "e"
        elif self.expression[-1] in "+-×÷^(":
            # 연산자나 괄호 뒤에는 그대로 추가
            self.expression += "e"
        elif self.expression[-1] in "0123456789.πe)":
            # 숫자나 상수 뒤에는 곱셈 연산자 추가
            self.expression += "×e"
        else:
            self.expression += "e"
        self.current_input = ''
    
    def rand_clicked(self):
        if self.calculator.random_used:
            return  # 이미 사용했으면 아무것도 하지 않음
            
        try:
            # 랜덤 값 생성
            rand_value = self.calculator.random()
            formatted_value = self.format_number(rand_value)
            
            if self.just_evaluated:
                self.expression = ""
                self.just_evaluated = False
                
            # 표현식이 0이거나 비어있으면 랜덤 값으로 대체
            if self.expression == "0" or self.expression == "":
                self.expression = formatted_value
            # 연산자로 끝나면 랜덤 값 추가
            elif self.expression[-1] in "+-×÷^(":
                self.expression += formatted_value
            else:
                # 기존 값이 있으면 랜덤 값으로 대체
                self.expression = formatted_value
                
            self.current_input = formatted_value
        except ValueError:
            # random_used가 True인 경우 (이미 처리됨)
            pass
    
    def ee_clicked(self):
        if self.current_input:
            self.expression += 'E'
            self.current_input = ''
    
    def memory_clear_clicked(self):
        self.calculator.memory_clear()
        # 메모리 버튼 색상 업데이트
        for i in range(self.layout().itemAt(1).count()):
            widget = self.layout().itemAt(1).itemAt(i).widget()
            if widget and widget.text() in ['mc', 'm+', 'm-', 'mr']:
                widget.setStyleSheet("""
                    QPushButton {
                        background-color: #2c2c2e;
                        color: #808080;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #3c3c3e;
                    }
                """)
    
    def memory_add_clicked(self):
        if self.current_input:
            value = float(self.current_input)
            self.calculator.memory_add(value)
            self.update_memory_buttons()
    
    def memory_subtract_clicked(self):
        if self.current_input:
            value = float(self.current_input)
            self.calculator.memory_subtract(value)
            self.update_memory_buttons()
    
    def memory_recall_clicked(self):
        result = self.calculator.memory_recall()
        formatted_result = self.format_number(result)
        self.current_input = formatted_result
        self.input = formatted_result
    
    def update_memory_buttons(self):
        # 메모리에 값이 있으면 버튼 색상 변경
        has_memory = self.calculator.memory != 0
        for i in range(self.layout().itemAt(1).count()):
            widget = self.layout().itemAt(1).itemAt(i).widget()
            if widget and widget.text() in ['mc', 'm+', 'm-', 'mr']:
                if has_memory:
                    widget.setStyleSheet("""
                        QPushButton {
                            background-color: #2c2c2e;
                            color: white;
                            font-size: 14px;
                        }
                        QPushButton:hover {
                            background-color: #3c3c3e;
                        }
                    """)
                else:
                    widget.setStyleSheet("""
                        QPushButton {
                            background-color: #2c2c2e;
                            color: #808080;
                            font-size: 14px;
                        }
                        QPushButton:hover {
                            background-color: #3c3c3e;
                        }
                    """)


def main():
    app = QApplication(sys.argv)
    calculator = EngineeringApp()
    calculator.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()