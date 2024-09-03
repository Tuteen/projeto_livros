from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton

class DialogoMensagem(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Mensagem para Correção')
        self.resize(300, 200)
        layout = QVBoxLayout(self)

        self.label = QLabel('Digite a mensagem para correção:')
        self.text_edit = QTextEdit()
        self.button_ok = QPushButton('OK')
        self.button_ok.clicked.connect(self.accept)

        layout.addWidget(self.label)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.button_ok)

    def get_mensagem(self):
        return self.text_edit.toPlainText()
