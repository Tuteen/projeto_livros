import sys
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit, QMessageBox, QCheckBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
import mysql.connector

class GerenciamentoCertidoes(QWidget):
    request_added = Signal()  # Sinal para notificar que uma solicitação foi adicionada ou modificada

    def __init__(self, db_config, usuario_atual, nome_completo):
        super().__init__()
        self.db_config = db_config
        self.usuario_atual = usuario_atual  # Nome do usuário logado
        self.nome_completo = nome_completo
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Gerenciamento de Certidões')
        self.setWindowIcon(QIcon('logo.png'))  # Ajuste o caminho do ícone
        self.resize(500, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
            }
            QLabel, QComboBox, QSpinBox {
                font-size: 14px;
                font-weight: bold;
            }
            QDateEdit {
                font-size: 16px;
                font-weight: bold;
            }
            QCheckBox {
                font-size: 16px;
                font-weight: bold;
            }
            QLineEdit, QComboBox, QSpinBox {
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
        self.setLayout(layout)

        # Inputs
        self.due_date_edit = QDateEdit(datetime.now())  # Set to current date
        self.due_date_edit.setCalendarPopup(True)

        book_layout = QHBoxLayout()
        self.type_input = QLineEdit()
        self.book_input = QLineEdit()
        self.page_input = QLineEdit()
        self.term_input = QLineEdit()

        self.name_input = QLineEdit()
        self.details_input = QLineEdit()
        self.urgency_checkbox = QCheckBox("Urgência")

        # Button
        self.add_button = QPushButton('Adicionar Solicitação')
        self.add_button.clicked.connect(self.add_request)

        layout.addWidget(QLabel('Data Necessária:'))
        layout.addWidget(self.due_date_edit)
        layout.addWidget(QLabel('Tipo/Livro/Folha/Termo:'))
        book_layout.addWidget(self.type_input)
        book_layout.addWidget(self.book_input)
        book_layout.addWidget(self.page_input)
        book_layout.addWidget(self.term_input)
        layout.addLayout(book_layout)
        layout.addWidget(QLabel('Nome do Registrado:'))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel('Detalhes:'))
        layout.addWidget(self.details_input)
        layout.addWidget(self.urgency_checkbox)
        layout.addWidget(self.add_button)

    def add_request(self):
        due_date = self.due_date_edit.date().toString(Qt.ISODate)
        book_info = f"{self.type_input.text().upper()} - {self.book_input.text()} / {self.page_input.text()} / {self.term_input.text()}"
        registrant_name = self.name_input.text()
        details = self.details_input.text()
        urgency = self.urgency_checkbox.isChecked()

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Certidoes (data_solicitacao, atendente, data_necessaria, livro_folha_termo, nome_registrado, detalhes, urgencia) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                       (datetime.now(), self.nome_completo, due_date, book_info, registrant_name, details, urgency))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Adicionado", "Solicitação adicionada com sucesso!")
        self.request_added.emit()  # Emitir sinal de atualização
        self.clear_inputs()

    def clear_inputs(self):
        # Clears the input fields after submission
        self.type_input.clear()
        self.book_input.clear()
        self.page_input.clear()
        self.term_input.clear()
        self.name_input.clear()
        self.details_input.clear()
        self.urgency_checkbox.setChecked(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'your_password',
        'database': 'your_database_name'
    }
    window = GerenciamentoCertidoes(db_config, 'Usuário1')
    window.show()
    sys.exit(app.exec())
