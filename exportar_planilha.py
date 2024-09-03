import sys
import mysql.connector
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDateEdit, QFileDialog, QMessageBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QDate
import pandas as pd

class TelaExportarPlanilha(QWidget):
    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Exportar Alterações para Planilha')
        self.setWindowIcon(QIcon('logo.png'))
        self.resize(400, 200)
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
            }
            QLabel, QPushButton, QDateEdit {
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

        main_layout = QVBoxLayout(self)

        date_layout = QHBoxLayout()
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)

        date_layout.addWidget(QLabel('Data Início:'))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel('Data Fim:'))
        date_layout.addWidget(self.end_date)
        main_layout.addLayout(date_layout)

        export_button = QPushButton('Exportar')
        export_button.clicked.connect(self.exportar_planilha)
        main_layout.addWidget(export_button)

        self.setLayout(main_layout)

    def exportar_planilha(self):
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        query = """
        SELECT t.data_modificacao, t.usuario_modificacao, f.numero_folha, l.numero
        FROM Termos t
        JOIN Folhas f ON t.id_folha = f.id
        JOIN Livros l ON f.id_livro = l.id
        WHERE t.data_modificacao BETWEEN %s AND %s
        ORDER BY t.data_modificacao
        """
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        conn.close()

        df = pd.DataFrame(rows, columns=['Data Modificação', 'Usuário Modificação', 'Número Folha', 'Número Livro'])

        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Excel Files (*.xlsx)")
        file_dialog.setDefaultSuffix("xlsx")

        if file_dialog.exec() == QFileDialog.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, 'Exportação Completa', 'Planilha exportada com sucesso!')
        else:
            QMessageBox.warning(self, 'Exportação Cancelada', 'A exportação foi cancelada.')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'sua_senha',
        'database': 'meu_banco'
    }
    window = TelaExportarPlanilha(db_config)
    window.show()
    sys.exit(app.exec())
