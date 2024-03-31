import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Set the background color of the window
        self.setStyleSheet("background-color: #ff00a2;")
        # Create buttons to run the Python files
        self.button1 = QPushButton("List", self)
        self.button1.setStyleSheet("background-color: #FFFFFF; color: #000000;")
        self.button1.clicked.connect(self.run_file1)
        self.button2 = QPushButton("Main", self)
        self.button2.setStyleSheet("background-color: #FFFFFF; color: #000000;")
        self.button2.clicked.connect(self.run_file2)
        self.button3 = QPushButton("AddDatatoDatabase", self)
        self.button3.setStyleSheet("background-color: #FFFFFF; color: #000000;")
        self.button3.clicked.connect(self.run_file3)
        self.button4 = QPushButton("EncodeGenerator", self)
        self.button4.setStyleSheet("background-color: #FFFFFF; color: #000000;")
        self.button4.clicked.connect(self.run_file4)
        self.button_exit = QPushButton("Exit", self)  # Thêm nút Exit
        self.button_exit.setStyleSheet("background-color: #FFFFFF; color: #000000;")
        self.button_exit.clicked.connect(self.exit_app)

        # Add the buttons to a vertical layout
        layout = QVBoxLayout()
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        layout.addWidget(self.button4)
        layout.addWidget(self.button_exit)
        self.setLayout(layout)

    def run_file1(self):
        # Run the Python file 1
        subprocess.run(['python', 'LoadDataFormFB.py'])

    def run_file2(self):
        # Run the Python file 2
        subprocess.run(['python', 'main.py'])

    def run_file3(self):
        # Run the Python file 3
        subprocess.run(['python', 'AddDatatoDatabase.py'])

    def run_file4(self):
        # Run the Python file 4
        subprocess.run(['python', 'EncodeGenerator.py'])
    def exit_app(self):
        # Thoát khỏi ứng dụng khi nhấn nút Exit
        QApplication.quit()    
    


if __name__ == '__main__':
    # Create a QApplication instance
    app = QApplication(sys.argv)

    # Create the main window and show it
    main_window = MainWindow()
    main_window.show()

    # Run the event loop
    sys.exit(app.exec_())
