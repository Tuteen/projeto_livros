import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QMessageBox, QSpacerItem, QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

class TelaPrincipal(QWidget):
    def __init__(self, nome_completo, usuario, nivel_acesso, controller=None, db_config=None):
        super().__init__()
        self.nome_completo = nome_completo
        self.usuario = usuario
        self.nivel_acesso = nivel_acesso
        self.controller = controller # Recebendo a referência do controlador
        self.db_config = db_config 
        self.menu_expanded = False  # Estado inicial do menu acordeão
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Grimório - Tela Principal')
        self.setWindowIcon(QIcon('logo.png'))  # Adicione o caminho real do ícone
        self.resize(600, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
            }
            QPushButton, QLabel {
                border: 2px solid #555;
                border-radius: 10px;
                padding: 5px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0081cb, stop:1 #00ccee);
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00ccee, stop:1 #0081cb);
            }
            QFrame {
                border: 1px solid #777;
                border-radius: 10px;
            }
        """)

        main_layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        self.user_button = QPushButton('👤')
        self.user_button.setFixedSize(40, 40)
        self.user_button.clicked.connect(self.toggle_menu)
        access_level = self.nivel_acesso
        self.user_label = QLabel(f'{self.nome_completo} - {access_level}')
        self.user_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_layout.addWidget(self.user_button, alignment=Qt.AlignTop)
        top_layout.addWidget(self.user_label, alignment=Qt.AlignTop)
        top_layout.addStretch()

        self.menu_frame = QFrame()
        self.menu_frame.setFixedWidth(180)
        self.menu_frame.setVisible(False)
        menu_layout = QVBoxLayout(self.menu_frame)

        edit_profile_button = QPushButton('Editar Perfil')
        edit_profile_button.clicked.connect(self.edit_user_profile)
        menu_layout.addWidget(edit_profile_button)
        
        if self.nivel_acesso == 'Admin':
            manage_users_button = QPushButton('Gerenciar Usuários')
            manage_users_button.clicked.connect(self.manage_users)
            menu_layout.addWidget(manage_users_button)
        
        logoff_button = QPushButton('Sair')
        logoff_button.clicked.connect(self.logoff)
        menu_layout.addWidget(logoff_button)

        main_layout.addWidget(self.menu_frame)

        content_layout = QVBoxLayout()
        spacer_top = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        spacer_bottom = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        insert_reg_button = QPushButton('Certidões para Inserir')
        insert_reg_button.clicked.connect(self.inserir_certidoes)
        create_book_button = QPushButton('Criar Livro')
        create_book_button.clicked.connect(self.criar_livro)
        list_books_button = QPushButton('Listar Livros')
        list_books_button.clicked.connect(self.listar_livros)
        batch_mark_button = QPushButton('Marcar em Lote')
        batch_mark_button.clicked.connect(self.marcar_em_lote)

        content_layout.addItem(spacer_top)
        content_layout.addWidget(insert_reg_button)
        content_layout.addWidget(create_book_button)
        content_layout.addWidget(list_books_button)   
        content_layout.addWidget(batch_mark_button)
        content_layout.addItem(spacer_bottom)
        main_layout.addLayout(content_layout)

    def toggle_menu(self):
        self.menu_expanded = not self.menu_expanded
        self.menu_frame.setVisible(self.menu_expanded)

    def manage_users(self):
        if self.controller:
            self.controller.show_gerenciar_usuarios()

    def logoff(self):
        if self.controller:
            self.controller.show_login()

    def edit_user_profile(self):
        if self.controller:
            self.controller.show_editar_perfil({'nome_usuario': self.usuario, 'nome_completo': self.nome_completo})
        
    def listar_livros(self):
        if self.controller:
            self.controller.show_listar_livros(self.usuario)

    def inserir_certidoes(self):
        if self.controller:
            self.controller.show_listar_certidoes(self.usuario, self.nome_completo)

    def criar_livro(self):
        if self.controller:
            self.controller.show_criar_livros(self)

    def marcar_em_lote(self):
        if self.controller:
            self.controller.show_marcar_em_lote(self.usuario)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = None  # Substitua isso pela instância real do controlador
    tela_principal = TelaPrincipal("Usuário1", "usuario1", "Admin", controller)
    tela_principal.show()
    sys.exit(app.exec())
