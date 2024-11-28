import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
                             QProgressBar, QMessageBox, QFrame, QStackedWidget, QHeaderView, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QIcon

from main import ph, adicionar_documento, obter_documentos_assinados, verificar_documento_no_banco

class AplicativoAssinadorDeDocumentos(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Assinador de Documentos Digital')
        self.setGeometry(100, 100, 1000, 500)
        
        layout_principal = QHBoxLayout(self)

        # Barra lateral de navegação
        layout_barra_lateral = QVBoxLayout()
        layout_barra_lateral.setAlignment(Qt.AlignTop)
        layout_barra_lateral.setSpacing(20)

        # Botão para "Assinar"
        self.botao_assinar = QPushButton("Assinar")
        self.botao_assinar.setIcon(QIcon('icons/assinar.png'))
        self.botao_assinar.setStyleSheet(self.estilo_botao_barra_lateral())
        self.botao_assinar.clicked.connect(self.mostrar_pagina_assinatura)
        layout_barra_lateral.addWidget(self.botao_assinar)

        # Botão para "Documentos Assinados"
        self.botao_documentos_assinados = QPushButton("Assinados")
        self.botao_documentos_assinados.setIcon(QIcon('icons/assinados.png'))
        self.botao_documentos_assinados.setStyleSheet(self.estilo_botao_barra_lateral())
        self.botao_documentos_assinados.clicked.connect(self.mostrar_pagina_documentos_assinados)
        layout_barra_lateral.addWidget(self.botao_documentos_assinados)
        
        quadro_barra_lateral = QFrame(self)
        quadro_barra_lateral.setLayout(layout_barra_lateral)
        quadro_barra_lateral.setFixedWidth(200)
        quadro_barra_lateral.setStyleSheet('background-color: #a29b9b;')

        # Área principal de conteúdo com páginas empilhadas
        self.widget_empilhado = QStackedWidget()
        
        # Página de Assinatura
        self.pagina_assinatura = QWidget()
        self.configurar_pagina_assinatura()
        self.widget_empilhado.addWidget(self.pagina_assinatura)

        # Página de Documentos Assinados
        self.pagina_documentos_assinados = QWidget()
        self.configurar_pagina_documentos_assinados()
        self.widget_empilhado.addWidget(self.pagina_documentos_assinados)

        # Adicionar a barra lateral e o conteúdo principal ao layout principal
        layout_principal.addWidget(quadro_barra_lateral)
        layout_principal.addWidget(self.widget_empilhado)
        
        self.setLayout(layout_principal)
    
    def estilo_botao_barra_lateral(self):
        return '''
            text-align: center;
            padding: 10px 20px;
            background-color: #d3c1e5;
            border: none;
            color: #444444;
            font-size: 14px;
            border-radius: 15px;
        '''

    def configurar_pagina_assinatura(self):
        layout_assinatura = QVBoxLayout()
        layout_assinatura.setAlignment(Qt.AlignTop)
        layout_assinatura.setSpacing(20)

        # Botão para upload de arquivos
        self.botao_importar = QPushButton("Importar arquivo")
        self.botao_importar.setIcon(QIcon('icons/documento.png'))
        self.botao_importar.setStyleSheet('text-align: center; padding: 10px 20px; background-color: #d3c1e5; border: none; color: #444444; font-size: 14px; border-radius: 15px;')
        self.botao_importar.clicked.connect(self.selecionar_arquivo)
        layout_assinatura.addWidget(self.botao_importar)

        # Lista de arquivos carregados
        self.lista_arquivos = QListWidget(self)
        self.lista_arquivos.setSelectionMode(QListWidget.SingleSelection)
        self.lista_arquivos.setStyleSheet('''
            QListWidget {
                background-color: #a29b9b; 
                color: #ffffff; 
                border: 1px solid #555555;
            }
            QListWidget::item {
                border: 2px solid #555555; /* Aumenta a borda do item */
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #555555; /* Cor de destaque ao selecionar */
                color: #ffffff;
            }
        ''')
        layout_assinatura.addWidget(self.lista_arquivos)

        # Barra de progresso
        self.barra_progresso = QProgressBar(self)
        self.barra_progresso.setVisible(False)
        layout_assinatura.addWidget(self.barra_progresso)

        # Botões de Assinar e Verificar
        self.botao_assinar_documento = QPushButton("Assinar")
        self.botao_verificar_documento = QPushButton("Verificar")

        self.botao_assinar_documento.setStyleSheet('background-color: #6a529f; color: #ffffff; padding: 10px; border-radius: 15px;')
        self.botao_verificar_documento.setStyleSheet('background-color: #d3c1e5; color: #6a529f; padding: 10px; border-radius: 15px;')

        self.botao_assinar_documento.clicked.connect(self.assinar_documento)
        self.botao_verificar_documento.clicked.connect(self.verificar_documento)

        layout_botoes = QHBoxLayout()
        layout_botoes.addWidget(self.botao_assinar_documento)
        layout_botoes.addWidget(self.botao_verificar_documento)
        
        layout_assinatura.addLayout(layout_botoes)
        
        self.pagina_assinatura.setLayout(layout_assinatura)
    
    def configurar_pagina_documentos_assinados(self):
        layout_documentos_assinados = QVBoxLayout()
        layout_documentos_assinados.setAlignment(Qt.AlignTop)
        layout_documentos_assinados.setSpacing(20)

        # Tabela de documentos assinados
        self.tabela_documentos_assinados = QTableWidget(self)
        self.tabela_documentos_assinados.setColumnCount(2)
        self.tabela_documentos_assinados.setHorizontalHeaderLabels(['Documento', 'Hash'])
        self.tabela_documentos_assinados.horizontalHeader().setStretchLastSection(True)
        self.tabela_documentos_assinados.horizontalHeader().setStyleSheet('color: #444444;')
        self.tabela_documentos_assinados.setStyleSheet('background-color: #a29b9b; color: #ffffff; border: 1px solid #555555;')
        self.tabela_documentos_assinados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout_documentos_assinados.addWidget(self.tabela_documentos_assinados)
        
        self.pagina_documentos_assinados.setLayout(layout_documentos_assinados)
    
    def mostrar_pagina_assinatura(self):
        self.widget_empilhado.setCurrentWidget(self.pagina_assinatura)
    
    def mostrar_pagina_documentos_assinados(self):
        self.widget_empilhado.setCurrentWidget(self.pagina_documentos_assinados)
        self.atualizar_tabela_documentos_assinados()

    def atualizar_tabela_documentos_assinados(self):
        self.tabela_documentos_assinados.setRowCount(0)  # Limpa as linhas existentes
        documentos = obter_documentos_assinados()
        for i, (caminho, hash_documento) in enumerate(documentos):
            self.tabela_documentos_assinados.insertRow(i)
            self.tabela_documentos_assinados.setItem(i, 0, QTableWidgetItem(os.path.basename(caminho)))
            self.tabela_documentos_assinados.setItem(i, 1, QTableWidgetItem(hash_documento))

    def selecionar_arquivo(self):
        opcoes = QFileDialog.Options()
        opcoes |= QFileDialog.DontUseNativeDialog
        arquivos, _ = QFileDialog.getOpenFileNames(self, "Escolha os arquivos", "", "Todos os Arquivos (*);;Arquivos de Texto (*.txt)", options=opcoes)
        if arquivos:
            for arquivo in arquivos:
                item = QListWidgetItem(os.path.basename(arquivo))
                item.setData(Qt.UserRole, arquivo)
                item.setSizeHint(QSize(0, 30))  # Aumenta o tamanho do item para visualizar a borda maior
                self.lista_arquivos.addItem(item)
            self.barra_progresso.setVisible(True)
            self.barra_progresso.setValue(100)
            self.barra_progresso.setVisible(False)

    def assinar_documento(self):
        itens_selecionados = self.lista_arquivos.selectedItems()
        if not itens_selecionados:
            QMessageBox.warning(self, "Erro", "Por favor, selecione um documento primeiro.")
            return
        
        for item in itens_selecionados:
            caminho = item.data(Qt.UserRole)
            resultado = verificar_documento_no_banco(caminho)
            if resultado:
                QMessageBox.warning(self, "Aviso", f"O documento '{os.path.basename(caminho)}' já foi assinado anteriormente. Apenas a verificação é permitida.")
                continue

            try:
                with open(caminho, "rb") as f:
                    conteudo = f.read()
                    salt = os.urandom(16)
                    hash_assinado = ph.hash(conteudo + salt)

                    adicionar_documento(caminho, hash_assinado, salt)

                QMessageBox.information(self, "Sucesso", f"Documento '{os.path.basename(caminho)}' assinado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao assinar o documento: {str(e)}")
    
    def verificar_documento(self):
        itens_selecionados = self.lista_arquivos.selectedItems()
        if not itens_selecionados:
            QMessageBox.warning(self, "Erro", "Por favor, selecione um documento primeiro.")
            return
        
        for item in itens_selecionados:
            caminho = item.data(Qt.UserRole)
            resultado = verificar_documento_no_banco(caminho)
            if not resultado:
                QMessageBox.warning(self, "Erro", f"O documento '{os.path.basename(caminho)}' não foi assinado previamente.")
                continue

            hash_original, salt = resultado
            try:
                with open(caminho, "rb") as f:
                    conteudo = f.read()
                    ph.verify(hash_original, conteudo + salt)

                QMessageBox.information(self, "Sucesso", f"O documento '{os.path.basename(caminho)}' é autêntico!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"O documento foi alterado!: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = AplicativoAssinadorDeDocumentos()
    janela.show()
    sys.exit(app.exec_())
