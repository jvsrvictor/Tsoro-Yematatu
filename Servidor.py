# IMPLEMENTAÇÃO DO JOGO TSORO YEMATATU - SERVIDOR
# AUTOR: JOSÉ VICTOR DA SILVA ROCHA
# 02/03/2022

import socket
import threading
from time import sleep
import sys
from PyQt5 import QtGui
from PyQt5 import QtWidgets, uic

# ----------------------------- VARIÁVEIS GLOBAIS -------------------------------- #

# CLIENTE REDE
SERVIDOR_IP = 'localhost'
PORTA = 8888
FORMATO = 'utf-8'
servidor = None

# VARIÁVEL PARA GERENCIAR OS TURNOS
jogou = False
jogou2 = False
empate = 0
fimDeJogo = False
fechaServidor = False

# LISTAS DE CLIENTES E SEUS NOMES
clientes = []
nomesClientes = []

t1 = None
t2 = None

# VETOR QUE REPRESENTA O TABULEIRO (1 = VERMELHO | 0 = AZUL | -7 = NENHUM)
tabuleiro = [-7 for x in range(7)]

# ELEMENTOS DA UI
listaJogadoresUI = None
fechaBtn = None
inciaBtn = None
endLbl = None
portLbl = None

# INICIAR O SERVIDOR
def iniciaServidor():
    global servidor, SERVIDOR_IP, PORTA
    global listaJogadoresUI, fechaBtn, inciaBtn, endLbl, portLbl, t1, t2, fimDeJogo, fechaServidor

    fimDeJogo = False
    fechaServidor = False

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #servidor.settimeout(0)
    servidor.bind((SERVIDOR_IP, PORTA))
    servidor.listen()

    inciaBtn.setEnabled(False)
    fechaBtn.setEnabled(True)
    endLbl.setText("Endereço: " + str(SERVIDOR_IP))
    portLbl.setText("Porta: " + str(PORTA))

    threading._start_new_thread(aceitaClientes, (servidor, " "))
    
# FECHA O SERVIDOR
def fechaServidor():
    global listaJogadoresUI, fechaBtn, inciaBtn, endLbl, portLbl, servidor, nomesClientes, clientes, t1, t2, fimDeJogo, fechaServidor
    fimDeJogo = True
    fechaServidor = True
    inciaBtn.setEnabled(True)
    fechaBtn.setEnabled(False)
    endLbl.setText("Endereço:")
    portLbl.setText("Porta:")
    listaJogadoresUI.clear()
    clientes = []
    nomesClientes = []
    servidor.close()

# ACEITA CLIENTES
def aceitaClientes(servidor, y):
    global fechaServidor, clientes
    while True:
        if (fechaServidor):
            break

        if len(clientes) == 0:
            cliente, addr = servidor.accept()
            cliente.settimeout(None)
            clientes.append(cliente)

            # INICIA THREADS PARA MANDAR E RECEBER MENSAGENS COM OS CLIENTES
            threading._start_new_thread(gerenciaPartida, ())
            threading._start_new_thread(mandaRecebeMensagemCliente, (cliente, addr))

        if len(clientes) == 1:
            cliente, addr = servidor.accept()
            cliente.settimeout(None)
            clientes.append(cliente)

            # INICIA THREADS PARA MANDAR E RECEBER MENSAGENS COM OS CLIENTES
            threading._start_new_thread(mandaRecebeMensagemCliente, (cliente, addr))
    return 0

# FUNÇÃO PARA MANDAR MENSAGEM PARA TODOS OS JOGADORES
def mandaMensagemPraTodos(mensagem):
    print("Mandou para todos:" + mensagem)
    global clientes
    for i in clientes:
        i.send(mensagem.encode('utf8'))

# FUNÇÃO PARA RECEBER MENSAGENS DO CLIENTE ATUAL E MANDAR PARA OS TODOS CLIENTES
def mandaRecebeMensagemCliente(conexaoCliente, ipcliente):
    global clientes, jogou, jogou2, nomesClientes, tabuleiro, empate, fimDeJogo

    # RECEBE NOME DO JOGADOR
    nomeCliente = conexaoCliente.recv(1024).decode('utf8')
    print("Recebeu mensagem: " + nomeCliente)

    # ATUALIZA A LISTA DE CLIENTES
    nomesClientes.append(nomeCliente)
    atualizaListaClientes(nomesClientes)

    # RECEBE E MANDA PARA TODOS AS MENSAGENS RECEBIDAS
    while True:
        # FIM DE JOGO - DESCONECTA AMBOS OS CLIENTES
        if(fimDeJogo):
            idx = retornaIndiceCliente(clientes, conexaoCliente)
            del nomesClientes[idx]
            del clientes[idx]
            conexaoCliente.close()
            atualizaListaClientes(nomesClientes)
            break

        mensagem = conexaoCliente.recv(1024).decode('utf8')
        print("Recebeu mensagem: " + mensagem)

        # SE FOR UMA MENSAGEM DE JOGADA, MUDA A VARIÁVEL GLOBAL JOGADA PARA PODER FAZER O GERENCIAMENTO DE TURNOS
        if(mensagem.startswith("J:")):
            jogou = True
            # ARMAZENAR A JOGADA NO VETOR TABULEIRO
            msgTemp = mensagem.replace("J:","")
            splittedMsg = msgTemp.split(":")
            indice = int(splittedMsg[0])
            tabuleiro[indice] = int(splittedMsg[1])

        elif(mensagem.startswith("DJ:")):
            jogou2 = True
            # RETIRA A JOGADA DO VETOR TABULEIRO
            indice = int(mensagem.replace("DJ:",""))
            tabuleiro[indice] = -7

        elif(mensagem.startswith("EM")):
            empate = empate + 1     

        # CLIENTE SE DESCONECTOU
        elif(not mensagem):
            idx = retornaIndiceCliente(clientes, conexaoCliente)
            del nomesClientes[idx]
            del clientes[idx]
            conexaoCliente.close()
            atualizaListaClientes(nomesClientes) 
            break       
        
        # MANDA A MENSAGEM PARA TODOS
        mandaMensagemPraTodos(mensagem)
    
    return 0

# FUNÇÃO QUE GERENCIA A PARTIDA E TURNOS
def gerenciaPartida():
    global clientes, jogou, jogou2, nomesClientes, fimDeJogo
    fimDeJogo = False
    
    # LOOP PARA ENVIAR E RECEBER JOGADAS
    while True:
        sleep(1)
        if(len(clientes) == 0):
            break
        # MANDA MENSAGEM INICIO DE PARTIDA PARA OS CLIENTES 
        if((len(clientes) == 2) and (len(nomesClientes) == 2)):
            # DEFINE QUEM SERÁ CADA COR (O PRIMEIRO A CONECTAR NO SERIDOR SEMPRE SERÁ VERMELHO)
            jogadorVermelho = clientes[0]
            jogadorAzul = clientes[1]
            nomeJogadorVermelho = nomesClientes[0]
            nomeJogadorAzul = nomesClientes[1]

            print(nomeJogadorVermelho)
            print(nomeJogadorAzul)

            # MENSAGEM DE INICIO DE PARTIDA
            mandaMensagemPraTodos("ST")
            sleep(0.5)

            # MANDA PARA O JOGADOR VERMELHO (O PRIMEIRO A ENTRAR), SUA COR
            stringV = "V"
            jogadorVermelho.send(stringV.encode('utf8'))
            print("Mandou para Vermelho: " + stringV)
            
            # MANDA PARA O JOGADOR AZUL (O ÚLTIMO A ENTRAR), SUA COR
            stringA = "A"
            jogadorAzul.send(stringA.encode('utf8'))
            print("Mandou para Azul: " + stringA)

            sleep(0.5)

            # MANDA O NOME DOS OPONENTES PARA OS JOGADORES,
            jogadorVermelho.send(nomeJogadorAzul.encode('utf8'))
            print("Mandou para Vermelho: " + nomeJogadorAzul)
            jogadorAzul.send(nomeJogadorVermelho.encode('utf8'))
            print("Mandou para Azul: " + nomeJogadorVermelho)
            
            sleep(2)

            # INICIO DAS RODADAS
            for i in range(3):
                # VEZ DO JOGADOR VERMELHO
                sleep(0.5)
                mandaMensagemPraTodos("JV")
                

                # VERIFICA SE O JOGADOR FEZ A JOGADA ANTES DE PARTIR PARA A PRÓXIMA
                while True:
                    if(jogou):
                        jogou = False
                        break

                if(verificaGanhador()!=-1):
                    break
                

                # VEZ DO JOGADOR AZUL
                sleep(0.5)
                mandaMensagemPraTodos("JA")

                # VERIFICA SE O JOGADOR FEZ A JOGADA ANTES DE PARTIR PARA A PRÓXIMA
                while True:
                    if(jogou):
                        jogou = False
                        break
                
                if(verificaGanhador()!=-1):
                    break

            # SE CHEGOU ATÉ AQUI É PORQUE HOUVE EMPATE
            # VERIFICA QUAL É A CASA VAZIA E RETORNA AS PEÇAS QUE PODEM SER MUDADAS
            # PARA ENTÃO LIBERAR O CLIQUE
            # A JOGADA DE EMPATE SE DARÁ DA SEGUINTE FORMA:
            # O JOGADOR CLICA NA PEÇA QUE DESEJA MOVER (ELA SOME) E CLICA ONDE VAI SER O SEU DESTINO (JOGADA NORMAL)
            # LOOP INFINITO QUE PARA QUANDO ALGUÉM GANHAR OU QUANDO DECIDIREM O EMPATE
            if(verificaGanhador()==-1):
                sleep(0.5)
                mandaMensagemPraTodos("EMBTN")
                while True:
                    # VEZ DO JOGADOR VERMELHO
                    sleep(0.5)
                    mandaMensagemPraTodos("JV")
                    sleep(0.5)
                    mandaPecasMoviveis(jogadorVermelho, 1)

                    # VERIFICA SE O JOGADOR FEZ A JOGADA ANTES DE PARTIR PARA A PRÓXIMA
                    while True:
                        if(jogou and jogou2):
                            jogou = jogou2 = False
                            break
                        if(empate==2):
                            sleep(0.5)
                            mandaMensagemPraTodos("EMPATE")
                            break
                    
                    if(empate==2):
                        break 

                    if(verificaGanhador()!=-1):
                        break
                    
                    # VEZ DO JOGADOR AZUL
                    sleep(0.5)
                    mandaMensagemPraTodos("JA")
                    sleep(0.5)
                    mandaPecasMoviveis(jogadorAzul, 0)

                    # VERIFICA SE O JOGADOR FEZ A JOGADA ANTES DE PARTIR PARA A PRÓXIMA
                    while True:
                        if(jogou and jogou2):
                            jogou = jogou2 = False
                            break
                        if(empate==2):
                            sleep(0.5)
                            mandaMensagemPraTodos("EMPATE")
                            break

                    if(empate==2):
                        break 
                    
                    if(verificaGanhador()!=-1):
                        break

            break     
    # FIM DE PARTIDA
    fimDeJogo = True
    return 0  
            
# FUNÇÃO QUE RETORNA CASAS DISPONÍVEIS PARA TROCA
def mandaPecasMoviveis(jogador, cor):
    global tabuleiro
    vetorDePecas = []
    casaVazia = tabuleiro.index(-7) # INDICE DA CASA VAZIA

    # FORMAS DE GANHAR (APENAS OS ÍNDICES)
    poss1 = [0,1,4]
    poss2 = [0,2,5]
    poss3 = [0,3,6]
    poss4 = [1,2,3]
    poss5 = [4,5,6]

    vetorDePecas.append(casaVazia)

    if (casaVazia in poss1):
        for i in poss1:
            # SÓ PODE MOVER A PRÓPRIA PEÇA
            if(tabuleiro[i] == cor):
                vetorDePecas.append(i)
    
    if (casaVazia in poss2):
        for i in poss2:
            # SÓ PODE MOVER A PRÓPRIA PEÇA
            if(tabuleiro[i] == cor):
                vetorDePecas.append(i)

    if (casaVazia in poss3):
        for i in poss3:
            # SÓ PODE MOVER A PRÓPRIA PEÇA
            if(tabuleiro[i] == cor):
                vetorDePecas.append(i)

    if (casaVazia in poss4):
        for i in poss4:
            # SÓ PODE MOVER A PRÓPRIA PEÇA
            if(tabuleiro[i] == cor):
                vetorDePecas.append(i)
    
    if (casaVazia in poss5):
        for i in poss5:
            # SÓ PODE MOVER A PRÓPRIA PEÇA
            if(tabuleiro[i] == cor):
                vetorDePecas.append(i)

    
    listaDePecas = list(dict.fromkeys(vetorDePecas))
    listaConvertidaString = [str(element) for element in listaDePecas]
    vetorEmString = ",".join(listaConvertidaString)

    mensagem = "RB:" + vetorEmString

    jogador.send(mensagem.encode('utf8'))
    print("Mandou para jogador:" + mensagem)
    
# FUNÇÃO QUE VERIFICA GANHADOR
def verificaGanhador():
    global tabuleiro

    # FORMAS DE GANHAR
    poss1 = tabuleiro[0] + tabuleiro[1] + tabuleiro[4]
    poss2 = tabuleiro[0] + tabuleiro[2] + tabuleiro[5]
    poss3 = tabuleiro[0] + tabuleiro[3] + tabuleiro[6]
    poss4 = tabuleiro[1] + tabuleiro[2] + tabuleiro[3]
    poss5 = tabuleiro[4] + tabuleiro[5] + tabuleiro[6]
    if(poss1*poss2*poss3*poss4*poss5 == 0):
        sleep(0.5)
        mandaMensagemPraTodos("G:"+str(0))
        return 0
    elif(poss1 == 3 or poss2 == 3 or poss3 == 3 or poss4 == 3 or poss5 == 3):
        sleep(0.5)
        mandaMensagemPraTodos("G:"+str(1))
        return 1
    else:
        return -1

# RETORNA O ÍNDICE DO CLIENTE ATUAL NA LISTA DOS CLIENTES
def retornaIndiceCliente(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx

# ATUALIZA A LISTA DE CLIENTES QUANDO UM NOVO CLIENTE CONECTA OU QUANDO ALGUM DESCONECTA
def atualizaListaClientes(name_list):
    global listaJogadoresUI
    listaJogadoresUI.clear()
    for i in name_list:
        listaJogadoresUI.addItem(i)

# ----------------------------- CLASSE DA UI -------------------------------- #

# CLASSE DA UI
class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method

        # Carrega o arquivo com a UI
        self.ui = uic.loadUi('Servidor.ui', self) # Load the .ui file
        self.setWindowIcon(QtGui.QIcon('Icon.png'))
        self.show()

        global listaJogadoresUI, fechaBtn, inciaBtn, endLbl, portLbl
        listaJogadoresUI = self.listaJogadores
        fechaBtn = self.fecharBTN
        inciaBtn = self.iniciarBTN
        endLbl = self.enderecoLBL
        portLbl = self.portaLBL

        inciaBtn.setEnabled(True)
        fechaBtn.setEnabled(False)

        # ASSOCIA AS FUNÇÕES PARA CADA BOTÃO
        inciaBtn.clicked.connect(iniciaServidor)
        fechaBtn.clicked.connect(fechaServidor)

# ----------------------------- MAIN -------------------------------- #

# MAIN
if __name__ == "__main__":
    # Cria uma instancia de QtWidgets.QApplication
    app = QtWidgets.QApplication(sys.argv) 

    # Cria uma instancia da classe UI
    window = Ui()

    # Inicia o programa
    sys.exit(app.exec())