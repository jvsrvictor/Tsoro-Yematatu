# IMPLEMENTAÇÃO DO JOGO TSORO YEMATATU - CLIENTE
# AUTOR: JOSÉ VICTOR DA SILVA ROCHA
# 02/03/2022


import socket
import threading
import sys
from time import sleep
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QMessageBox

# ----------------------------- VARIÁVEIS GLOBAIS -------------------------------- #

# CLIENTE REDE
SERVIDOR_IP = 'localhost'
PORTA = 8888
FORMATO = 'utf-8'

# NOME DO JOGADOR E DO OPONENTE
seuNome = ""
nomeOponente = ""

# COR DO JOGADOR (TRUE = VERMELHO | FALSE = AZUL)
minhaCor = True

# CORES DOS JOGADORES
vermelhoBTN = "rgba(194, 39, 45, 255)"
azulBTN = "rgba(40, 112, 194, 255)"
vermelhoBTNh = "rgba(194, 39, 45, 200)"
azulBTNh = "rgba(40, 112, 194, 200)"
transparente = "rgba(0, 0, 0, 0)"

# ----------------------------- CLASSES DA UI -------------------------------- #

# Classe UI Inicial
class Ui(QtWidgets.QMainWindow):
    # CONSTRUTOR
    def __init__(self):
        super(Ui, self).__init__()

        self.setWindowTitle("Tsoro Yematatu")

        # Carrega o arquivo com a UI
        self.ui = uic.loadUi('DigiteNome.ui', self) # Load the .ui file

        # INSTANCIA A CLASSE DO TABULEIRO EM SEGUNDO PLANO
        self.game = UiGame()

        # PERMITE O ACIONAMENTO DO BOTÃO COM A TECLA 'ENTER'
        self.nomeInput.returnPressed.connect(lambda: self.__conectaServidor())

        # ASSOCIA AS FUNÇÕES PARA CADA BOTÃO
        self.confirmaNome.clicked.connect(lambda: self.__conectaServidor())
  
    # CONECTA COM O SERVIDOR
    def __conectaServidor(self):
        if(self.nomeInput.text() != ""):
            try:
                global cliente, seuNome
                seuNome = self.nomeInput.text()
                cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cliente.connect((SERVIDOR_IP, PORTA))
                cliente.settimeout(None)
                cliente.send(seuNome.encode("utf8")) # Send nome to server after connecting

                # AGUARDA PELO PELO OPONENTE
                self.aguardando.setStyleSheet("color: rgba(0, 153, 10, 255)")
                self.nomeInput.setEnabled(False)
                self.confirmaNome.setEnabled(False)    

                # INICIA UM THREAD PARA CONTINUAR RECEBENDO MENSAGENS
                threading._start_new_thread(self.__recebeMensagemServidor,())

            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowIcon(QtGui.QIcon('Icon.png'))
                msg.setWindowTitle("Tsoro Yematatu")
                msg.setText("Erro ao conectar com o servidor!")
                retval = msg.exec()


    # FUNÇÃO PRINCIPAL DE COMUNICAÇÃO COM O SERVIDOR
    def __recebeMensagemServidor(self):
        global cliente, seuNome, minhaCor, nomeOponente

        while True:
            from_server = cliente.recv(1024).decode('utf8')
            # RECEBE A MENSAGEM DE INICIO DE PARTIDA
            if (from_server =="ST"):
                print("Recebeu mensagem:" + from_server)

                # MOSTRA PARA O JOGADOR COM QUAL COR ELE IRÁ JOGAR
                cor = cliente.recv(1024).decode('utf8')
                print("Recebeu mensagem:" + cor)
                nomeOponente = cliente.recv(1024).decode('utf8')
                print("Recebeu mensagem:" + nomeOponente)
                
                if(cor=="V"):                  
                    widgetA.addWidget(self.game)
                    widgetA.setCurrentIndex(widgetA.currentIndex()+1)
                    self.game.textoServidor.setText("VOCÊ JOGA COM AS VERMELHAS")
                    self.game.textoServidor.setStyleSheet("color: " + vermelhoBTN + ";")
                    self.game.setCorUI(True)
                    break
                else:
                    widgetA.addWidget(self.game)
                    widgetA.setCurrentIndex(widgetA.currentIndex()+1)
                    self.game.textoServidor.setText("VOCÊ JOGA COM AS AZUIS")
                    self.game.textoServidor.setStyleSheet("color: " + azulBTN + ";")
                    self.game.setCorUI(False)
                    break

                

        # LOOP INFINITO PARA RECEBER AS MENSAGENS DO SERVIDOR
        while True:
            
            #from_server = cliente.recv(1024).decode('utf8')


            from_server = cliente.recv(1024).decode('utf8')
            print("Recebeu mensagem:" + from_server)

            if not from_server: break

            # RECEBE MENSAGEM CHAT
            if (from_server.startswith("MSG:")):
                self.game.chatArea.addItem(from_server.replace("MSG:", ""))
                self.game.chatArea.scrollToBottom()

            # SISTEMA DE PARTIDAS
            if(from_server=="JV" and minhaCor==True):
                self.game.textoServidor.setText("SUA VEZ!")
                self.game.textoServidor.setStyleSheet("color: " + vermelhoBTN + ";")
                self.game.ativaBTNS()
                
            elif(from_server=="JA" and minhaCor==False):
                self.game.textoServidor.setText("SUA VEZ!")
                self.game.textoServidor.setStyleSheet("color: " + azulBTN + ";")
                self.game.ativaBTNS()
                
            elif((from_server=="JV" and minhaCor==False)):
                self.game.textoServidor.setText("VEZ DE " + nomeOponente.upper() + "!")
                self.game.textoServidor.setStyleSheet("color: " + vermelhoBTN + ";")
                self.game.desativaBTNS()

            elif((from_server=="JA" and minhaCor==True)):
                self.game.textoServidor.setText("VEZ DE " + nomeOponente.upper() + "!")
                self.game.textoServidor.setStyleSheet("color: " + azulBTN + ";")
                self.game.desativaBTNS()
                
            # RECEBE AS JOGADAS DO SERVIDOR E DESENHA NO TABULEIRO
            if (from_server.startswith("J:")):
                self.game.desenhaJogada(from_server)

            # RECEBE AS JOGADAS DO SERVIDOR E DESENHA NO TABULEIRO
            if (from_server.startswith("DJ:")):
                self.game.desenhaDesfazJogada(from_server)

            # RECEBE AS JOGADAS DO SERVIDOR E DESENHA NO TABULEIRO
            if (from_server.startswith("RB:")):
                self.game.reativaBTNS(from_server)

            # RECEBE A LIBERAÇÃO DO EMPATE
            if (from_server.startswith("EMBTN")):
                self.game.empateBTN.setEnabled(True)
            
            # RECEBE A SOLICITAÇÃO DE EMPATE
            if (from_server.startswith("EM:")):
                self.game.empate(from_server)

            # RECEBE A SOLICITAÇÃO DE EMPATE
            if (from_server.startswith("EMPATE")):
                self.game.textoServidor.setText("EMPATE!")
                self.game.textoServidor.setStyleSheet("color: rgba(0, 0, 0, 255) ;")
                self.game.desativaBTNS()
                sleep(5)
                break

            # RECEBE QUEM GANHOU
            if (from_server.startswith("G:")):
                self.game.desativaBTNS()
                if(from_server.replace("G:", "")=="1"):
                    if(minhaCor==int(from_server.replace("G:", ""))):
                        self.game.textoServidor.setText("VOCÊ GANHOU!")
                        self.game.textoServidor.setStyleSheet("color: " + vermelhoBTN + ";")
                        sleep(5)
                        break
                        
                    else:
                        self.game.textoServidor.setText(nomeOponente.upper() + " GANHOU!")
                        self.game.textoServidor.setStyleSheet("color: " + vermelhoBTN + ";")
                        sleep(5)
                        break
                else:
                    if(minhaCor==int(from_server.replace("G:", ""))):
                        self.game.textoServidor.setText("VOCÊ GANHOU!")
                        self.game.textoServidor.setStyleSheet("color: " + azulBTN + ";")
                        sleep(5)
                        break
                    else:
                        self.game.textoServidor.setText(nomeOponente.upper() + " GANHOU!")
                        self.game.textoServidor.setStyleSheet("color: " + azulBTN + ";")
                        sleep(5)
                        break
                
        cliente.close()
        app.exit()

     
# Classe UI + Tabuleiro
class UiGame(QtWidgets.QMainWindow):
    def __init__(self):
        super(UiGame, self).__init__() # Call the inherited classes __init__ method

        # Carrega o arquivo com a UI
        self.ui = uic.loadUi('MainGame.ui', self) # Load the .ui file

        self.textInput.returnPressed.connect(lambda: self.enviaMensagemChat())

        # Botões como variáveis
        BTN0 = self.pos0
        BTN1 = self.pos1
        BTN2 = self.pos2
        BTN3 = self.pos3
        BTN4 = self.pos4
        BTN5 = self.pos5
        BTN6 = self.pos6

        # GERENCIAMENTO DE PEÇAS E TABULEIRO
        self.tabuleiroBTN = [BTN0,BTN1,BTN2,BTN3,BTN4,BTN5,BTN6]
        self.casasLivres = [True for x in range(7)] # TRUE = LIVRE | FALSE = OCUPADO
        self.casaVazia = None

        tabuleiroBG = QPixmap("TabuleiroBG.png")
        item = QtWidgets.QGraphicsPixmapItem(tabuleiroBG)
        tabuleiroSceneUI = QGraphicsScene()
        tabuleiroSceneUI.addItem(item)
        self.tabuleiro.setScene(tabuleiroSceneUI)

        self.sendText.clicked.connect(lambda: self.enviaMensagemChat())

        BTN0.clicked.connect(lambda: self.jogada(0, minhaCor))
        BTN1.clicked.connect(lambda: self.jogada(1, minhaCor))
        BTN2.clicked.connect(lambda: self.jogada(2, minhaCor))
        BTN3.clicked.connect(lambda: self.jogada(3, minhaCor))
        BTN4.clicked.connect(lambda: self.jogada(4, minhaCor))
        BTN5.clicked.connect(lambda: self.jogada(5, minhaCor))
        BTN6.clicked.connect(lambda: self.jogada(6, minhaCor))

        self.empateBTN.clicked.connect(lambda: self.enviaEmpate())

        self.desativaBTNS()

    def enviaEmpate(self):
        global cliente
        if(minhaCor):
            MSG = "EM:1"
        else:
            MSG = "EM:2"

        cliente.send(MSG.encode("utf8"))
        self.empateBTN.setEnabled(False)

    # SETA A COR DE HOVER DAS PEÇAS DO TABULEIRO
    def setCorUI(self, cor):
        global minhaCor
        indexBTN = 0
        if(cor):
            for i in self.tabuleiroBTN:
                i.setStyleSheet("#pos" + str(indexBTN) + ":hover{ border: none; border-radius: 13px; background-color: " + vermelhoBTN + ";} #pos" + str(indexBTN) + "{ border: none; border-radius: 13px; background-color: " + transparente + ";}")
                indexBTN = indexBTN + 1
        else:
            minhaCor = cor
            for i in self.tabuleiroBTN:
                i.setStyleSheet("#pos" + str(indexBTN) + ":hover{ border: none; border-radius: 13px; background-color: " + azulBTN + ";} #pos" + str(indexBTN) + "{ border: none; border-radius: 13px; background-color: " + transparente + ";}")
                indexBTN = indexBTN + 1

    # DESABILITA TODOS OS BOTÕES (USADO NA VEZ DO OPONENTE)
    def desativaBTNS(self):
        for i in self.tabuleiroBTN:
            i.setEnabled(False)

    # HABILITA TODOS OS BOTÕES (USADO NA VEZ DO OPONENTE)
    def ativaBTNS(self):
        index=0
        for i in self.tabuleiroBTN:
            if(self.casasLivres[index]):
                i.setEnabled(True)
            index = index + 1

    # REATIVA DETERMINADOS BOTÕES
    def reativaBTNS(self, msg):
        global minhaCor
        msgTemp = msg.replace("RB:","")
        splittedMsg = msgTemp.split(",")
        self.casaVazia = int(splittedMsg[0])

        # DESATIVA O BOTÃO VAZIO INICIAL
        self.tabuleiroBTN[self.casaVazia].setEnabled(False)
        splittedMsg.pop(0)

        for i in splittedMsg:
            self.tabuleiroBTN[int(i)].setEnabled(True)
            if(minhaCor):
                self.tabuleiroBTN[int(i)].setStyleSheet("#pos" + i + ":hover{ border: none; border-radius: 13px; background-color: " + vermelhoBTNh + ";} #pos" + i + "{ border: none; border-radius: 13px; background-color: " + vermelhoBTN + ";}")
            else:
                self.tabuleiroBTN[int(i)].setStyleSheet("#pos" + i + ":hover{ border: none; border-radius: 13px; background-color: " + azulBTNh + ";} #pos" + i + "{ border: none; border-radius: 13px; background-color: " + azulBTN + ";}")

    def empate(self, msg):
        global minhaCor
        msgTemp = msg.replace("EM:","")
        if((int(msgTemp) == 1 and minhaCor) or (int(msgTemp) == 0 and not minhaCor)):
            self.empateBTN.setText("VOCÊ SOLICITOU EMPATE!")
            self.empateBTN.setEnabled(False)
        else:
            self.empateBTN.setText(nomeOponente.upper() + " SOLICITOU EMPATE!")

    # ----------------------------- UI + GAMEPLAY -------------------------------- #

    # DESENHA A JOGADA RECEBIDA PELO SERVIDOR
    def desenhaJogada(self, msg):
        msgTemp = msg.replace("J:","")
        splittedMsg = msgTemp.split(":")
        indice = splittedMsg[0]
        cor = int(splittedMsg[1])
        if(cor == 1):
            self.tabuleiroBTN[int(indice)].setStyleSheet("#pos" + str(indice) + "{background-color: " + vermelhoBTN + "; border: none; border-radius: 13px;}")
        else:
            self.tabuleiroBTN[int(indice)].setStyleSheet("#pos" + str(indice) + "{background-color: " + azulBTN + "; border: none; border-radius: 13px;}")

        # DESATIVA O BOTÃO
        self.tabuleiroBTN[int(indice)].setEnabled(False) 

        # TIRA ELE DA LISTA DE CASAS DISPONÍVEIS
        self.casasLivres[int(indice)] = False

    # REALIZA A JOGADA E ENVIA PARA O SERVIDOR
    def jogada(self, indice, cor):
        global cliente

        if(self.casasLivres[int(indice)]):
            if(cor):
                corStr = "1"
            else:
                corStr = "0"
            # JOGADA
            jogada = "J:" + str(indice) + ":" + corStr
        else:
            # DESFAZ JOGADA
            jogada = "DJ:" + str(indice)
            # REATIVA O BOTÃO VAZIO INICIAL
            self.tabuleiroBTN[self.casaVazia].setEnabled(True)

        # MANDA PARA O SERVIDOR A JOGADA,E O SERVIDOR MANDA O DESENHA JOGADA
        cliente.send(jogada.encode("utf8"))

    # ---------------------------------------------------------------------------- #

    # DESENHA A JOGADA DESFEITA RECEBIDA PELO SERVIDOR
    def desenhaDesfazJogada(self, msg):
        indice = int(msg.replace("DJ:",""))

        # ATIVA O BOTÃO
        # tabuleiroBTN[int(indice)].setEnabled(True) 
        if(minhaCor):
            self.tabuleiroBTN[indice].setStyleSheet("#pos" + str(indice) + ":hover{ border: none; border-radius: 13px; background-color: " + vermelhoBTN + ";} #pos" + str(indice) + "{ border: none; border-radius: 13px; background-color: " + transparente + ";}")
        else:
            self.tabuleiroBTN[indice].setStyleSheet("#pos" + str(indice) + ":hover{ border: none; border-radius: 13px; background-color: " + azulBTN + ";} #pos" + str(indice) + "{ border: none; border-radius: 13px; background-color: " + transparente + ";}")
        
        # READICIONA ELE NA LISTA DE CASAS DISPONÍVEIS
        self.casasLivres[indice] = True

    # FUNÇÃO PARA ENVIAR CHAT
    def enviaMensagemChat(self):
        global cliente, seuNome
        mensagem = self.textInput.text()
        if(mensagem!=""):
            MSG = "MSG:" + seuNome.upper() + ": " + mensagem
            self.textInput.clear()
            # MANDA PARA O SERVIDOR A JOGADA,E O SERVIDOR MANDA O DESENHA JOGADA
            cliente.send(MSG.encode("utf8"))

# ----------------------------- MAIN -------------------------------- #

# MAIN
if __name__ == "__main__":

    # Cria uma instancia de QtWidgets.QApplication
    app = QtWidgets.QApplication(sys.argv) 
    widgetA = QtWidgets.QStackedWidget()
    

    # Cria uma instancia da classe UI
    mainWindow = Ui()
    widgetA.addWidget(mainWindow)
    widgetA.setWindowTitle("Tsoro Yematatu")
    widgetA.setWindowIcon(QtGui.QIcon('Icon.png'))
    widgetA.show()

    # Inicia o programa
    sys.exit(app.exec())
