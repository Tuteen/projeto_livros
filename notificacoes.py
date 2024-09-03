import sys
import mysql.connector
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QDialog, QComboBox, QTextEdit, QMessageBox
)
from PySide6.QtGui import QIcon, QColor, QBrush
from PySide6.QtCore import Qt

class SistemaNotificacoes(QWidget):
    def __init__(self, db_config, usuario_atual):
        super().__init__()
        self.db_config = db_config
        self.usuario_atual = usuario_atual
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Sistema de Notificações')
        self.setWindowIcon(QIcon('notificacoes_icon.png'))
        self.resize(600, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
            }
            QLabel, QPushButton, QComboBox, QTextEdit {
                font-size: 14px;
                font-weight: bold;
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
            QListWidget {
                background: #222;
                border: none;
                color: white;
                font-size: 14px;
                padding: 5px;
            }
        """)

        main_layout = QVBoxLayout(self)

        # Botão para enviar nova mensagem
        enviar_button = QPushButton('Nova Mensagem')
        enviar_button.clicked.connect(self.enviar_mensagem)
        main_layout.addWidget(enviar_button, alignment=Qt.AlignTop)

        # Lista de notificações
        self.lista_notificacoes = QListWidget()
        self.lista_notificacoes.itemClicked.connect(self.mostrar_mensagem)
        main_layout.addWidget(self.lista_notificacoes)
        
        # Carregar notificações
        self.carregar_notificacoes()

        self.setLayout(main_layout)

    def carregar_notificacoes(self):
        self.lista_notificacoes.clear()
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        query = """
        SELECT remetente, mensagem, data_envio, lida
        FROM Notificacoes
        WHERE destinatario = %s
        ORDER BY data_envio DESC
        """
        cursor.execute(query, (self.usuario_atual,))
        results = cursor.fetchall()
        print(f"Mensagens recebidas por {self.usuario_atual}: {results}")  # Print para depuração
        for remetente, mensagem, data_envio, lida in results:
            item = QListWidgetItem(f"{data_envio} - {remetente}")
            item.setData(Qt.UserRole, mensagem)  # Armazena a mensagem no item
            item.setData(Qt.UserRole + 1, data_envio)  # Armazena a data de envio no item
            item.setData(Qt.UserRole + 2, remetente)  # Armazena o remetente no item
            print(f"Mensagem: {mensagem}, Lida: {lida}")  # Print para depuração
            if lida == 0:  # Verificação explícita para não lidas
                print(f"Mensagem não lida: {mensagem}")  # Print para depuração
                item.setBackground(QBrush(QColor("#FF0000")))  # Cor vermelha para não lidas
                item.setForeground(QBrush(QColor("#FFFFFF")))  # Define a cor do texto como branco para contraste
            else:
                item.setBackground(QBrush(QColor("#444")))  # Cor padrão para lidas
                item.setForeground(QBrush(QColor("#FFFFFF")))
            self.lista_notificacoes.addItem(item)

        conn.close()
        
    def mostrar_mensagem(self, item):
        mensagem = item.data(Qt.UserRole)
        QMessageBox.information(self, 'Mensagem', mensagem)
        # Marcar como lida
        data_envio = item.data(Qt.UserRole + 1)  # Recupera a data de envio do item
        remetente = item.data(Qt.UserRole + 2)  # Recupera o remetente do item
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE Notificacoes 
        SET lida = TRUE 
        WHERE destinatario = %s AND remetente = %s AND data_envio = %s
        """, (self.usuario_atual, remetente, data_envio))
        conn.commit()
        conn.close()
        self.carregar_notificacoes()  # Recarregar notificações para atualizar a cor

    def enviar_mensagem(self):
        self.dialogo_envio = DialogoEnvioMensagem(self.db_config, self.usuario_atual)
        self.dialogo_envio.exec_()

class DialogoEnvioMensagem(QDialog):
    def __init__(self, db_config, remetente):
        super().__init__()
        self.db_config = db_config
        self.remetente = remetente
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Enviar Mensagem')
        self.setWindowIcon(QIcon('notificacoes_icon.png'))
        self.resize(400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
            }
            QLabel, QPushButton, QComboBox, QTextEdit {
                font-size: 14px;
                font-weight: bold;
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

        self.destinatario_input = QComboBox()
        self.carregar_usuarios()
        self.mensagem_input = QTextEdit()
        enviar_button = QPushButton('Enviar')
        enviar_button.clicked.connect(self.enviar_mensagem)

        layout.addWidget(QLabel('Enviar para:'))
        layout.addWidget(self.destinatario_input)
        layout.addWidget(QLabel('Mensagem:'))
        layout.addWidget(self.mensagem_input)
        layout.addWidget(enviar_button)

        self.setLayout(layout)

    def carregar_usuarios(self):
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT nome_completo FROM Usuarios WHERE nome_completo != %s", (self.remetente,))
        for (nome_completo,) in cursor.fetchall():
            self.destinatario_input.addItem(nome_completo)

        conn.close()

    def enviar_mensagem(self):
        destinatario = self.destinatario_input.currentText()
        mensagem = self.mensagem_input.toPlainText()

        if not mensagem:
            QMessageBox.warning(self, 'Erro', 'A mensagem não pode estar vazia.')
            return

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        query = """
        INSERT INTO Notificacoes (remetente, destinatario, mensagem, data_envio, lida)
        VALUES (%s, %s, %s, NOW(), FALSE)
        """
        cursor.execute(query, (self.remetente, destinatario, mensagem))
        conn.commit()
        conn.close()

        QMessageBox.information(self, 'Mensagem Enviada', 'Sua mensagem foi enviada com sucesso.')
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'sua_senha',
        'database': 'meu_banco'
    }
    window = SistemaNotificacoes(db_config, "usuario1")
    window.show()
    sys.exit(app.exec())
