from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QApplication, QHeaderView, QLineEdit, QCheckBox, QSystemTrayIcon, QMenu)
from PySide6.QtGui import QColor, QIcon
from PySide6.QtCore import Qt, QTimer
import mysql.connector
from datetime import datetime, date
from certidoes import GerenciamentoCertidoes

def format_datetime(date_input):
    if isinstance(date_input, datetime):
        return date_input.strftime('%d/%m/%Y %H:%M:%S')
    elif isinstance(date_input, date):
        return date_input.strftime('%d/%m/%Y')
    try:
        return datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S.%f').strftime('%d/%m/%Y %H:%M:%S')
    except ValueError:
        try:
            return datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
        except ValueError:
            return datetime.strptime(date_input, '%Y-%m-%d').strftime('%d/%m/%Y')

class ListaCertidoes(QWidget):
    def __init__(self, db_config, usuario_atual, nome_completo):
        super().__init__()
        self.db_config = db_config
        self.usuario_atual = usuario_atual
        self.nome_completo = nome_completo
        self.last_row_count = self.obter_quantidade_certidoes()  # Inicializa com a quantidade atual de certidões
        self.initUI()
        self.setup_tray_icon()
        self.setup_timer()

    def initUI(self):
        self.setWindowTitle('Lista de Certidões Solicitadas')
        self.setWindowIcon(QIcon('logo.png'))
        self.resize(1200, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
            }
            QLabel, QPushButton, QTableWidget, QLineEdit, QCheckBox {
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
            QHeaderView::section {
                background-color: #555;
                padding: 4px;
                border: 1px solid #333;
                font-size: 14px;
                font-weight: bold;
            }""")
        main_layout = QVBoxLayout(self)
        filter_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Digite para buscar...")
        self.search_bar.textChanged.connect(self.carregar_certidoes)
        filter_layout.addWidget(self.search_bar)

        self.chk_mostrar_concluidos = QCheckBox("Mostrar Concluídos")
        self.chk_mostrar_concluidos.stateChanged.connect(self.carregar_certidoes)
        filter_layout.addWidget(self.chk_mostrar_concluidos)

        self.chk_mostrar_urgentes = QCheckBox("Mostrar Urgentes")
        self.chk_mostrar_urgentes.stateChanged.connect(self.carregar_certidoes)
        filter_layout.addWidget(self.chk_mostrar_urgentes)

        self.btn_solicitar = QPushButton('Solicitar Certidão')
        self.btn_solicitar.clicked.connect(self.abrir_solicitacao_certidao)
        filter_layout.addWidget(self.btn_solicitar, alignment=Qt.AlignRight)

        main_layout.addLayout(filter_layout)

        self.table_certidoes = QTableWidget(0, 8)
        self.table_certidoes.setHorizontalHeaderLabels(['Data Solicitação', 'Atendente', 'Data Necessária', 'Livro/Folha/Termo', 'Nome Registrado', 'Detalhes', 'Urgência', 'Status'])
        self.table_certidoes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_certidoes.itemClicked.connect(self.mostrar_dialogo_conclusao)
        main_layout.addWidget(self.table_certidoes)

        self.carregar_certidoes()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon('logo.png'), self)
        tray_menu = QMenu(self)
        restore_action = tray_menu.addAction("Restore")
        restore_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.instance().quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.verificar_novas_solicitacoes)
        self.timer.start(30000)  # Verificar a cada 30 segundos

    def verificar_novas_solicitacoes(self):
        current_row_count = self.obter_quantidade_certidoes()
        if current_row_count > self.last_row_count:
            self.carregar_certidoes()
            self.last_row_count = current_row_count
            if not self.isActiveWindow() or self.isMinimized():
                self.tray_icon.showMessage("Nova Solicitação", "Há uma nova solicitação de certidão.", QSystemTrayIcon.Information, 5000)
                QApplication.alert(self)

    def obter_quantidade_certidoes(self):
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Certidoes")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def abrir_solicitacao_certidao(self):
        self.solicitar_certidao = GerenciamentoCertidoes(self.db_config, self.usuario_atual, self.nome_completo)
        self.solicitar_certidao.show()
        self.solicitar_certidao.request_added.connect(self.carregar_certidoes)

    def carregar_certidoes(self):
        search_text = self.search_bar.text().strip().lower()
        show_concluded = self.chk_mostrar_concluidos.isChecked()
        show_urgent = self.chk_mostrar_urgentes.isChecked()

        self.table_certidoes.setRowCount(0)
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        query = """
            SELECT id, data_solicitacao, atendente, data_necessaria, livro_folha_termo, nome_registrado, detalhes, urgencia, concluido
            FROM Certidoes
            WHERE (LOWER(data_solicitacao) LIKE %s OR
                  LOWER(atendente) LIKE %s OR
                  LOWER(data_necessaria) LIKE %s OR
                  LOWER(livro_folha_termo) LIKE %s OR
                  LOWER(nome_registrado) LIKE %s OR
                  LOWER(detalhes) LIKE %s)
        """
        conditions = ['%' + search_text + '%'] * 6
        if not show_concluded:
            query += " AND concluido = 0"
        if show_urgent:
            query += " AND urgencia = 1"
        cursor.execute(query, conditions)
        for certidao in cursor.fetchall():
            row_position = self.table_certidoes.rowCount()
            self.table_certidoes.insertRow(row_position)
            for i, item in enumerate(certidao[1:]):
                cell = QTableWidgetItem(format_datetime(item) if i in [0, 2] else str(item))
                cell.setData(Qt.UserRole, certidao[0])
                cell.setToolTip(str(item))  # Tooltip to show all content
                if i == 6:
                    cell.setText('Urgente' if item else 'Normal')
                if i == 7:
                    cell.setText('Concluído' if item else 'Pendente')
                self.table_certidoes.setItem(row_position, i, cell)
                if certidao[7] and not certidao[8]:
                    cell.setBackground(QColor("#FF6347"))
                if certidao[8]:
                    cell.setBackground(QColor("#006400"))
        conn.close()

    def mostrar_dialogo_conclusao(self, item):
        if self.table_certidoes.item(item.row(), 7).text() == 'Pendente':
            resposta = QMessageBox.question(self, "Concluir Certidão", "Marcar esta certidão como concluída?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if resposta == QMessageBox.Yes:
                self.marcar_como_concluido(item.row())

    def marcar_como_concluido(self, row):
        certidao_id = self.table_certidoes.item(row, 0).data(Qt.UserRole)
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        cursor.execute("UPDATE Certidoes SET concluido = 1 WHERE id = %s", (certidao_id,))
        conn.commit()
        conn.close()
        self.carregar_certidoes()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    db_config = {'host': 'localhost', 'user': 'your_username', 'password': 'your_password', 'database': 'your_database_name'}
    window = ListaCertidoes(db_config, "usuario1", "Nome Completo")
    window.show()
    sys.exit(app.exec_())
