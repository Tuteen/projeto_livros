from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

class DialogMarcarCorrecao(QDialog):
    def __init__(self, item):
        super().__init__()
        self.item = item
        self.mensagem = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Marcar para Correção')

        self.layout = QVBoxLayout()

        self.label = QLabel(f'Marcar {self.item.text()} para correção:')
        self.layout.addWidget(self.label)

        self.input_mensagem = QLineEdit()
        self.input_mensagem.setPlaceholderText('Descreva a correção necessária...')
        self.layout.addWidget(self.input_mensagem)

        self.botoes = QHBoxLayout()
        self.botao_ok = QPushButton('OK')
        self.botao_ok.clicked.connect(self.aceitar)
        self.botoes.addWidget(self.botao_ok)

        self.botao_cancelar = QPushButton('Cancelar')
        self.botao_cancelar.clicked.connect(self.reject)
        self.botoes.addWidget(self.botao_cancelar)

        self.layout.addLayout(self.botoes)
        self.setLayout(self.layout)

    def aceitar(self):
        self.mensagem = self.input_mensagem.text()
        self.accept()
