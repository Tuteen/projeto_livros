import mysql.connector
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QLineEdit, QCheckBox, QMessageBox,
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt

class MarcarEmLote(QWidget):
    def __init__(self, nome_completo, db_config, nivel_acesso):
        super().__init__()
        self.usuario_atual = nome_completo
        self.db_config = db_config
        self.nivel_acesso = nivel_acesso# Adicionando configuração do banco de dados
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
            QLabel, QComboBox, QSpinBox, QCheckBox {
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton, QLineEdit{
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
        self.bookTypeCombo.addItems(self.get_book_type_options())
        layout.addWidget(QLabel('Tipo de Livro:'))
        layout.addWidget(self.bookTypeCombo)

        self.bookNumberEdit = QLineEdit()
        layout.addWidget(QLabel('Número do Livro:'))
        layout.addWidget(self.bookNumberEdit)
        self.bookNumberEdit.setPlaceholderText("ex: 001, 002")
        self.startPageEdit = QLineEdit()
        layout.addWidget(QLabel('Página Inicial:'))
        layout.addWidget(self.startPageEdit)
        self.startPageEdit.setPlaceholderText("Inicio do intervalo")
        self.endPageEdit = QLineEdit()
        layout.addWidget(QLabel('Página Final:'))
        layout.addWidget(self.endPageEdit)
        self.endPageEdit.setPlaceholderText("Final do intervalo")
        self.markAllCheckbox = QCheckBox("Marcar Todo o Livro")



        layout.addWidget(self.endPageEdit)
        layout.addWidget(self.markAllCheckbox)

        self.markButton = QPushButton('Marcar em Lote')
        self.markButton.clicked.connect(self.mark_in_batch)
        layout.addWidget(self.markButton)
        
    def get_book_type_options(self):
        if self.nivel_acesso == 'Admin':
            return ['NASCIMENTO (LIVRO A)', 'CASAMENTO CIVIL (LIVRO B)', 'CAS. REL. CIVIL (LIVRO BA)',
                    'ÓBITO (LIVRO C)', 'NATIMORTO (LIVRO CA)', 'PROCLAMAS (LIVRO D)',
                    'PROCURAÇÕES (LIVRO P)', 'SUBSTABELECIMENTOS (LIVRO S)', 'ESCRITURAS DE COMPRA E VENDA (LIVRO N)',
                    'ESCRITURAS DIVERSAS (LIVRO TD)', 'TESTAMENTO (LIVRO T)']
        elif self.nivel_acesso == 'Tabelionato':
            return ['PROCURAÇÕES (LIVRO P)', 'SUBSTABELECIMENTOS (LIVRO S)', 'ESCRITURAS DE COMPRA E VENDA (LIVRO N)',
                    'ESCRITURAS DIVERSAS (LIVRO TD)', 'TESTAMENTO (LIVRO T)']
        elif self.nivel_acesso == 'Registro Civil':
            return ['NASCIMENTO (LIVRO A)', 'CASAMENTO CIVIL (LIVRO B)', 'CAS. REL. CIVIL (LIVRO BA)',
                    'ÓBITO (LIVRO C)', 'NATIMORTO (LIVRO CA)', 'PROCLAMAS (LIVRO D)']
        else:
            return []

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

