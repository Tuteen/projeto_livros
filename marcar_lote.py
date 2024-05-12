import sys
import mysql.connector
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QLineEdit, QCheckBox, QMessageBox,
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt

class MarcarEmLote(QWidget):
    def __init__(self, usuario_atual, db_config):
        super().__init__()
        self.usuario_atual = usuario_atual
        self.db_config = db_config  # Adicionando configuração do banco de dados
        self.setWindowTitle('Marcar em Lote')
        self.resize(400, 300)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.setWindowIcon(QIcon('logo.png'))
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
            }
            QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox {
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

        self.bookTypeCombo = QComboBox()
        self.bookTypeCombo.addItems([
            'NASCIMENTO (LIVRO A)', 'CASAMENTO CIVIL (LIVRO B)', 'CAS. REL. CIVIL (LIVRO BA)',
            'ÓBITO (LIVRO C)', 'NATIMORTO (LIVRO CA)', 'PROCLAMAS (LIVRO D)',
            'PROCURAÇÕES (LIVRO P)', 'SUBSTABELECIMENTOS (LIVRO S)',
            'ESCRITURAS DE COMPRA E VENDA (LIVRO N)', 'ESCRITURAS DIVERSAS (LIVRO TD)',
            'TESTAMENTO (LIVRO T)'
        ])
        layout.addWidget(self.bookTypeCombo)

        self.bookNumberEdit = QLineEdit()
        self.bookNumberEdit.setPlaceholderText("Número do Livro (ex: 001, 002)")
        self.startPageEdit = QLineEdit()
        self.startPageEdit.setPlaceholderText("Página Inicial")
        self.endPageEdit = QLineEdit()
        self.endPageEdit.setPlaceholderText("Página Final")
        self.markAllCheckbox = QCheckBox("Marcar Todo o Livro")

        layout.addWidget(self.bookNumberEdit)
        layout.addWidget(self.startPageEdit)
        layout.addWidget(self.endPageEdit)
        layout.addWidget(self.markAllCheckbox)

        self.markButton = QPushButton('Marcar em Lote')
        self.markButton.clicked.connect(self.mark_in_batch)
        layout.addWidget(self.markButton)

    def mark_in_batch(self):
        book_type = self.bookTypeCombo.currentText()
        book_number = self.bookNumberEdit.text()
        start_page = self.startPageEdit.text()
        end_page = self.endPageEdit.text()
        mark_all = self.markAllCheckbox.isChecked()

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        try:
            if mark_all:
                query = """
                UPDATE Termos
                SET digitalizado = 1, usuario_modificacao = %s, data_modificacao = NOW()
                WHERE id_folha IN (
                    SELECT f.id
                    FROM Folhas f
                    JOIN Livros l ON f.id_livro = l.id
                    WHERE l.tipo = %s AND l.numero = %s
                )"""
                cursor.execute(query, (self.usuario_atual, book_type, book_number))
            else:
                query = """
                UPDATE Termos
                SET digitalizado = 1, usuario_modificacao = %s, data_modificacao = NOW()
                WHERE id_folha IN (
                    SELECT f.id
                    FROM Folhas f
                    JOIN Livros l ON f.id_livro = l.id
                    WHERE l.tipo = %s AND l.numero = %s AND f.numero_folha BETWEEN %s AND %s
                )"""
                cursor.execute(query, (self.usuario_atual, book_type, book_number, start_page, end_page))
            conn.commit()
            QMessageBox.information(self, "Sucesso", "Marcação em lote realizada com sucesso!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao marcar em lote: {e}")
        finally:
            conn.close()

