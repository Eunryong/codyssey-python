import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

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
                    self.values[i] = self.multiply(self.values[i] * self.values[i + 1])
                elif self.operators[i] == '÷':
                    self.values[i] = self.divide(self.values[i] / self.values[i + 1])
                self.values.pop(i + 1)
                self.operators.pop(i)
            else:
                i += 1

        i = 0
        while i < len(self.operators):
            if self.operators[i] in ['+', '-']:
                if self.operators[i] == '+':
                    self.values[i] = self.add(self.values[i] * self.values[i + 1])
                elif self.operators[i] == '-':
                    self.values[i] = self.subtract(self.values[i] / self.values[i + 1])
                self.values.pop(i + 1)
                self.operators.pop(i)
            else:
                i += 1
        
        if len(self.operators) == 0:
            return self.values[0]

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
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('계산기')
        self.setGeometry(300, 300, 300, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: white;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555;
                border-radius: 5px;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
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
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
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
        self.display.setText(self.input)
    
    def number_clicked(self, number):
        if number == '.':
            if self.current_input == '':
                self.current_input = '0.'
                self.input += self.current_input
            else:
                self.current_input += '' if number in self.current_input else number
                self.input += '' if number in self.current_input else number
        else:
            if self.calculator.compare_value_operator():
                self.current_input = number
            else:
                self.current_input += number
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
            
            if result == int(result):
                result = int(result)
            
            self.display.setText(str(result))
            self.operator = ""

            
        except ZeroDivisionError:
            self.display.setText("0")
            self.calculator.reset()
            self.clear()
    
    def clear_clicked(self):
        self.clear()
    
    def clear(self):
        self.calculator.reset()
        self.current_input = '0'
        self.display.setText(self.current_input)
        self.input = "0"

    
    def plus_minus_clicked(self):
        if self.current_input != "0" and len(self.current_input) != 0:
            value = float(self.current_input)
            self.calculator.negative_positive(value)
            self.input = self.input[:len(self.current_input) * -1] + '-' + self.current_input
            self.display.setText(self.input)
    
    def percent_clicked(self):
        self.calculator.percent()
        value = self.calculator.get_value()
        if value == int(value):
            value = int(value)
        self.display.setText(str(value))

def main():
    app = QApplication(sys.argv)
    calculator = App()
    calculator.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()