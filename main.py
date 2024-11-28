import os
from argon2 import PasswordHasher
import sqlite3

# Função para criar ou conectar ao banco de dados SQLite
def conectar_banco():
    conn = sqlite3.connect('documentos.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS documentos (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      caminho TEXT NOT NULL UNIQUE,
                      hash TEXT NOT NULL,
                      salt TEXT NOT NULL)''')
    conn.commit()
    return conn

# Função para adicionar um documento ao banco de dados
def adicionar_documento(caminho, hash_assinado, salt):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO documentos (caminho, hash, salt) VALUES (?, ?, ?)', 
                   (caminho, hash_assinado, salt))
    conn.commit()
    conn.close()

# Função para obter todos os documentos assinados do banco de dados
def obter_documentos_assinados():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('SELECT caminho, hash FROM documentos')
    documentos = cursor.fetchall()
    conn.close()
    return documentos

# Função para verificar se o documento está no banco de dados
def verificar_documento_no_banco(caminho):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('SELECT hash, salt FROM documentos WHERE caminho = ?', (caminho,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# Inicializa o hasher Argon2
ph = PasswordHasher()
