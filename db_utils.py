import sqlite3
import hashlib

def hash_password(password):
    """ Retorna a hash SHA-256 da senha fornecida. """
    sha_signature = hashlib.sha256(password.encode()).hexdigest()
    return sha_signature

def insert_user(username, password, access_level):
    """ Insere um usuário no banco de dados com senha criptografada. """
    hashed_password = hash_password(password)  # Criptografa a senha
    conn = sqlite3.connect('meu_banco.db')  # Conecta ao banco de dados
    cursor = conn.cursor()
    
    # Cria uma consulta SQL para inserir o usuário
    sql = """
    INSERT INTO usuarios (nome_usuario, senha, nivel_acesso)
    VALUES (?, ?, ?);
    """
    try:
        # Executa a consulta SQL
        cursor.execute(sql, (username, hashed_password, access_level))
        conn.commit()  # Confirma as alterações no banco de dados
        print("Usuário inserido com sucesso!")
    except sqlite3.IntegrityError as e:
        print("Erro ao inserir usuário:", e)
    finally:
        conn.close()  # Fecha a conexão com o banco de dados

# Exemplo de uso
insert_user('teste', 'teste123', 'Usuario')

