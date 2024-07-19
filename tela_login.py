import sys
import hashlib
import mysql.connector
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

class TelaLogin(QWidget):
    def __init__(self, controller=None, db_config=None):
        super().__init__()
        self.controller = controller
        self.db_config = db_config  # Configurações do banco de dados passadas como dicionário
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Grimório - Login')
        self.setWindowIcon(QIcon('logo.png'))  # Certifique-se de ajustar o caminho do ícone conforme necessário
        self.resize(350, 250)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit {
                border: 2px solid #555;
                border-radius: 10px;
                padding: 5px;
                background: #444;
                color: white;
            }
            QPushButton {
                border: 2px solid #555;
                border-radius: 10px;
                padding: 6px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0081cb, stop:1 #00ccee);
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00ccee, stop:1 #0081cb);
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # User label and line edit
        label_usuario = QLabel('Usuário:')
        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText('Digite seu usuário')

        # Password label and line edit
        label_senha = QLabel('Senha:')
        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText('Digite sua senha')
        self.input_senha.setEchoMode(QLineEdit.Password)

        self.input_usuario.returnPressed.connect(self.check_password)
        self.input_senha.returnPressed.connect(self.check_password)
        
        # Login button
        btn_login = QPushButton('Login')
        btn_login.clicked.connect(self.check_password)

        # Add widgets to layout
        layout.addWidget(label_usuario)
        layout.addWidget(self.input_usuario)
        layout.addWidget(label_senha)
        layout.addWidget(self.input_senha)
        layout.addWidget(btn_login)

        self.setLayout(layout)

    def clear_fields(self):
        self.input_usuario.clear()
        self.input_senha.clear()

    def check_password(self):
        usuario = self.input_usuario.text()
        senha = self.input_senha.text()

        if not usuario or not senha:
            QMessageBox.warning(self, "Erro de Login", "Por favor, preencha todos os campos.")
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT senha, nivel_acesso FROM usuarios WHERE nome_usuario = %s", (usuario,))
            user_data = cursor.fetchone()

            if user_data:
                stored_password, nivel_acesso = user_data
                if hashlib.sha256(senha.encode()).hexdigest() == stored_password:
                    cursor.execute("SELECT nome_completo FROM usuarios WHERE nome_usuario = %s", (usuario,))
                    nome_completo = cursor.fetchone()
                    if nome_completo:
                        nome_completo = nome_completo[0]
                    conn.close()
                    self.controller.show_principal(nome_completo, usuario, nivel_acesso)
                else:
                    conn.close()
                    QMessageBox.warning(self, "Erro de Login", "Senha incorreta.")
            else:
                conn.close()
                QMessageBox.warning(self, "Erro de Login", "Usuário não encontrado.")
        except mysql.connector.Error as err:
            QMessageBox.warning(self, "Erro de Banco de Dados", f"Erro ao conectar ao banco de dados: {err}")
            if conn.is_connected():
                conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': '#Tuteen2001',
        'database': 'meu_banco'
    }
    login = TelaLogin(db_config=db_config)
    login.show()
    sys.exit(app.exec())
