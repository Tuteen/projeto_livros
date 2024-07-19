import mysql.connector
import hashlib
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt

def hash_password(password):
    """ Retorna a hash SHA-256 da senha fornecida. """
    sha_signature = hashlib.sha256(password.encode()).hexdigest()
    return sha_signature

class EditarPerfil(QWidget):
    def __init__(self, usuario, db_config):
        super().__init__()
        self.db_config = db_config
        self.usuario = usuario  # Usuário logado
        self.setWindowTitle('Editar Perfil')
        self.setWindowIcon(QIcon('logo.png'))
        self.resize(600, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
            }
            QLabel, QPushButton, QLineEdit {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QPushButton {
                border: 2px solid #555;
                border-radius: 10px;
                padding: 5px;
                background: #444;
                color: white;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0081cb, stop:1 #00ccee);
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00ccee, stop:1 #0081cb);
            }
        """)

        # Campos de edição para usuário logado
        self.editUsername = QLineEdit(self.usuario['nome_usuario'])
        self.editFullName = QLineEdit(self.usuario['nome_completo'])
        self.editPassword = QLineEdit()
        self.editPassword.setPlaceholderText("Nova Senha (opcional)")
        self.editPassword.setEchoMode(QLineEdit.Password)  # Ocultar caracteres
        self.editConfirmPassword = QLineEdit()
        self.editConfirmPassword.setPlaceholderText("Confirmar Nova Senha")
        self.editConfirmPassword.setEchoMode(QLineEdit.Password)  # Ocultar caracteres

        layout.addWidget(QLabel("Nome de Usuário:"))
        layout.addWidget(self.editUsername)
        layout.addWidget(QLabel("Nome Completo:"))
        layout.addWidget(self.editFullName)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.editPassword)
        layout.addWidget(QLabel("Confirmar Senha:"))
        layout.addWidget(self.editConfirmPassword)

        # Botão para salvar as alterações
        btnSave = QPushButton('Salvar Alterações')
        btnSave.clicked.connect(self.save_changes)
        layout.addWidget(btnSave)

    def save_changes(self):
        username = self.editUsername.text()
        full_name = self.editFullName.text()
        password = self.editPassword.text()
        confirm_password = self.editConfirmPassword.text()

        if password and password != confirm_password:
            QMessageBox.warning(self, "Erro", "As senhas não coincidem.")
            return

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            if password:
                hashed_password = hash_password(password)
                cursor.execute("UPDATE usuarios SET nome_usuario=%s, nome_completo=%s, senha=%s WHERE nome_usuario=%s",
                               (username, full_name, hashed_password, self.usuario['nome_usuario']))
            else:
                cursor.execute("UPDATE usuarios SET nome_usuario=%s, nome_completo=%s WHERE nome_usuario=%s",
                               (username, full_name, self.usuario['nome_usuario']))
            conn.commit()
            QMessageBox.information(self, "Sucesso", "Perfil atualizado com sucesso!")
            self.close()
        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Erro", f"Erro ao atualizar perfil: {str(e)}")
        finally:
            conn.close()

