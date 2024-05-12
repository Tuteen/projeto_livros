import sys
import mysql.connector
import hashlib
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QComboBox
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt

def hash_password(password):
    """ Retorna a hash SHA-256 da senha fornecida. """
    sha_signature = hashlib.sha256(password.encode()).hexdigest()
    return sha_signature

class GerenciamentoUsuarios(QWidget):
    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config
        self.setWindowTitle('Gerenciamento de Usuários')
        self.resize(900, 600)
        self.selected_user_id = None  # Inicializa como None para evitar referência antes de atribuição
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Gerenciamento de Usuários')
        self.setWindowIcon(QIcon('logo.png'))
        self.resize(900, 600)
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
        layout = QVBoxLayout(self)

        self.btnAddUser = QPushButton('Adicionar Novo Usuário')
        self.btnAddUser.clicked.connect(self.add_user)
        layout.addWidget(self.btnAddUser)

        self.userList = QListWidget()
        self.userList.itemClicked.connect(self.user_selected)
        layout.addWidget(self.userList)

        self.editUsername = QLineEdit()
        self.editFullName = QLineEdit()
        self.editPassword = QLineEdit()
        self.comboAccessLevel = QComboBox()
        self.comboAccessLevel.addItems(["Admin", "Usuário"])

        self.editUsername.setPlaceholderText("Nome de usuário")
        self.editFullName.setPlaceholderText("Nome completo")
        self.editPassword.setPlaceholderText("Senha")

        layout.addWidget(self.editUsername)
        layout.addWidget(self.editFullName)
        layout.addWidget(self.editPassword)
        layout.addWidget(self.comboAccessLevel)

        self.btnSave = QPushButton('Salvar Alterações')
        self.btnSave.clicked.connect(self.save_changes)
        layout.addWidget(self.btnSave)

        self.load_users()

    def add_user(self):
        username = self.editUsername.text()
        password = self.editPassword.text()
        access_level = self.comboAccessLevel.currentText()
        full_name = self.editFullName.text()

        if username and password and access_level and full_name:
            hashed_password = hash_password(password)
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO usuarios (nome_usuario, senha, nivel_acesso, nome_completo) VALUES (%s, %s, %s, %s)",
                    (username, hashed_password, access_level, full_name)
                )
                conn.commit()
                QMessageBox.information(self, "Sucesso", "Usuário inserido com sucesso!")
                self.load_users()
                self.selected_user_id = cursor.lastrowid
            except mysql.connector.Error as e:
                QMessageBox.warning(self, "Erro", f"Erro ao inserir usuário: {str(e)}")
            finally:
                conn.close()
        else:
            QMessageBox.warning(self, "Erro", "Todos os campos devem ser preenchidos!")

    def user_selected(self, item):
        self.selected_user_id = item.data(Qt.UserRole)
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT nome_usuario, nome_completo, nivel_acesso FROM usuarios WHERE id_usuario=%s", (self.selected_user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.editUsername.setText(user[0])
            self.editFullName.setText(user[1])
            self.comboAccessLevel.setCurrentText(user[2])
            self.editPassword.clear()

    def save_changes(self):
        if self.selected_user_id:
            username = self.editUsername.text()
            password = self.editPassword.text()
            access_level = self.comboAccessLevel.currentText()
            full_name = self.editFullName.text()

            if username and access_level and full_name:
                conn = mysql.connector.connect(**self.db_config)
                cursor = conn.cursor()
                try:
                    if password:
                        hashed_password = hash_password(password)
                        cursor.execute("UPDATE usuarios SET nome_usuario=%s, senha=%s, nivel_acesso=%s, nome_completo=%s WHERE id_usuario=%s",
                                       (username, hashed_password, access_level, full_name, self.selected_user_id))
                    else:
                        cursor.execute("UPDATE usuarios SET nome_usuario=%s, nivel_acesso=%s, nome_completo=%s WHERE id_usuario=%s",
                                       (username, access_level, full_name, self.selected_user_id))
                    conn.commit()
                    QMessageBox.information(self, "Sucesso", "Usuário atualizado com sucesso!")
                    self.load_users()
                except mysql.connector.Error as e:
                    QMessageBox.warning(self, "Erro", f"Erro ao atualizar usuário: {str(e)}")
                finally:
                    conn.close()
            else:
                QMessageBox.warning(self, "Erro", "Nome de usuário, nome completo e nível de acesso são obrigatórios!")
        else:
            QMessageBox.warning(self, "Erro", "Nenhum usuário selecionado!")

    def load_users(self):
        self.userList.clear()
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nome_usuario FROM usuarios")
        for user_id, username in cursor.fetchall():
            item = QListWidgetItem(f"{username}")
            item.setData(Qt.UserRole, user_id)
            self.userList.addItem(item)
        conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_config = {'host': 'localhost', 'user': 'your_username', 'password': 'your_password', 'database': 'your_database_name'}
    window = GerenciamentoUsuarios(db_config)
    window.show()
    sys.exit(app.exec())
