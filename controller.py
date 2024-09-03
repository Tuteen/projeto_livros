import sys
import os
import json
from cryptography.fernet import Fernet
import mysql.connector
from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit
from tela_login import TelaLogin
from tela_principal import TelaPrincipal
from criar_livro import CriarLivro
from listar_livros import TelaListarLivros
from gerenciar_usuarios import GerenciamentoUsuarios
from editar_perfil import EditarPerfil
from marcar_lote import MarcarEmLote
from lista_certidoes import ListaCertidoes
from relatorios import ModuloRelatorios
from notificacoes import SistemaNotificacoes

class AppController:
    def __init__(self, app):
        self.app = app
        self.db_config = self.load_db_config()
        self.tela_login = TelaLogin(controller=self, db_config=self.db_config)
        self.tela_principal = None
        self.tela_editar_perfil = None

    def generate_key(self):
        """ Generates a key and instantiate a cipher suite """
        key = Fernet.generate_key()
        with open('secret.key', 'wb') as key_file:
            key_file.write(key)
        return key

    def load_key(self):
        """ Load the previously generated key """
        return open('secret.key', 'rb').read()

    def encrypt_data(self, data, key):
        """ Encrypt the data with the given key """
        data = json.dumps(data).encode('utf-8')
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(data)
        return cipher_text

    def decrypt_data(self, cipher_text, key):
        """ Decrypt the data with the given key """
        cipher_suite = Fernet(key)
        decrypted_data = cipher_suite.decrypt(cipher_text)
        return json.loads(decrypted_data.decode('utf-8'))

    def load_db_config(self):
        """ Check if the encrypted config file exists and load it.
        If it does not exist, prompt the user to enter config and create it.
        """
        config_path = 'db_config.enc'
        if os.path.exists(config_path):
            key = self.load_key()
            with open(config_path, 'rb') as enc_file:
                encrypted_data = enc_file.read()
            db_config = self.decrypt_data(encrypted_data, key)
            return db_config
        else:
            db_config = {
                'host': '127.0.0.1',
                'user': 'root',
                'password': '',
                'database': 'meu_banco'
            }
            db_config['host'], ok = QInputDialog.getText(None, 'Configuração do BD', 'Host:')
            if not ok: sys.exit()
            db_config['user'], ok = QInputDialog.getText(None, 'Configuração do BD', 'Usuário:')
            if not ok: sys.exit()
            db_config['password'], ok = QInputDialog.getText(None, 'Configuração do BD', 'Senha:', QLineEdit.Password)
            if not ok: sys.exit()
            db_config['database'], ok = QInputDialog.getText(None, 'Configuração do BD', 'Nome do BD:')
            if not ok: sys.exit()

            key = self.generate_key()
            encrypted_data = self.encrypt_data(db_config, key)
            with open(config_path, 'wb') as enc_file:
                enc_file.write(encrypted_data)
            return db_config

    def start(self):
        self.show_login()
        
    def show_login(self):
        if self.tela_principal:
            self.tela_principal.close()
            self.tela_login.clear_fields()
        self.tela_login.show()

    def show_principal(self, nome_completo, usuario, nivel_acesso):
        self.usuario_atual = usuario
        self.nome_completo = nome_completo
        self.nivel_acesso = nivel_acesso
        self.tela_login.close()
        if self.tela_principal:
            self.tela_principal.close()
        self.tela_principal = TelaPrincipal(nome_completo, usuario, nivel_acesso, controller=self, db_config=self.db_config)
        self.tela_principal.show()

    def show_criar_livros(self, usuario):
        if hasattr(self, 'criar_livro'):
            self.criar_livro.close()
        self.criar_livro = CriarLivro(controller=self, db_config=self.db_config, usuario_atual=self.usuario_atual, nivel_acesso=self.nivel_acesso)
        self.criar_livro.show()

    def show_listar_livros(self, usuario):
        self.listar_livro = TelaListarLivros(db_config=self.db_config, nome_completo=self.nome_completo, nivel_acesso=self.nivel_acesso)
        self.listar_livro.show()

    def show_editar_perfil(self, usuario):
        if self.tela_editar_perfil is not None:
            self.tela_editar_perfil.close()
        self.tela_editar_perfil = EditarPerfil(usuario, db_config=self.db_config)
        self.tela_editar_perfil.show()
    
    def show_notificacoes(self, usuario):
        self.notificacoes = SistemaNotificacoes(db_config=self.db_config, usuario_atual=self.nome_completo)
        self.notificacoes.show()

    def show_gerenciar_usuarios(self):
        self.gerenciar_usuarios = GerenciamentoUsuarios(db_config=self.db_config)
        self.gerenciar_usuarios.show()

    def show_marcar_em_lote(self, nome_completo):
        self.marcar_em_lote = MarcarEmLote(nome_completo= self.nome_completo, db_config=self.db_config, nivel_acesso= self.nivel_acesso)
        self.marcar_em_lote.show()

    def show_listar_certidoes(self, usuario, nome_completo):
        self.listar_certidoes = ListaCertidoes(db_config=self.db_config, usuario_atual=self.usuario_atual, nome_completo=self.nome_completo)
        self.listar_certidoes.show()

    def show_relatorios(self):
        self.relatorios = ModuloRelatorios(self.db_config)
        self.relatorios.show()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = AppController()
    controller.start()
    controller.run()
