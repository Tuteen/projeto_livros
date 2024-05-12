import mysql.connector
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

class DialogoDigitalizacao(QDialog):
    def __init__(self, parent, termo_id, usuario_atual):
        super().__init__(parent)
        self.termo_id = termo_id
        self.usuario_atual = usuario_atual  # Usuário logado
        
        # Obter o último usuário que modificou o termo
        self.ultimo_usuario_modificacao = self.get_last_modified_user()
        
        self.initUI()
    
    def get_last_modified_user(self):
        conn = mysql.connector.connect(**self.parent().db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT usuario_modificacao FROM Termos WHERE id = %s", (self.termo_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "Desconhecido"

    def initUI(self):
        self.setWindowTitle('Opções de Digitalização')
        layout = QVBoxLayout(self)

        # Label para mostrar o usuário que fez a última modificação
        self.usuario_label = QLabel(f'Última modificação por: {self.ultimo_usuario_modificacao}')
        layout.addWidget(self.usuario_label)

        # Botões para ação
        btn_digitalizado = QPushButton('Digitalizado')
        btn_digitalizado.clicked.connect(self.marcar_digitalizado)
        btn_averbado = QPushButton('Averbado')
        btn_averbado.clicked.connect(self.marcar_averbado)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_digitalizado)
        btn_layout.addWidget(btn_averbado)
        layout.addLayout(btn_layout)

    def marcar_digitalizado(self):
        self.alterar_status_digitalizado(True)
        self.close()

    def marcar_averbado(self):
        self.alterar_status_digitalizado(True, True)
        self.close()

    def alterar_status_digitalizado(self, digitalizado, averbado=False):
        conn = mysql.connector.connect(**self.parent().db_config)
        cursor = conn.cursor()
        update_query = "UPDATE Termos SET digitalizado = %s, usuario_modificacao = %s, data_modificacao = CURRENT_TIMESTAMP WHERE id = %s"
        cursor.execute(update_query, (digitalizado, self.usuario_atual, self.termo_id))
        conn.commit()
        conn.close()
        self.parent().carregar_livros()  # Recarrega os dados para refletir a mudança
