import socket
import socketserver
import threading
import pickle
import game
import gui
from game.multi import MessagePacker as Packer, MessageParser as Parser, Message

PORT = 31500

class TCPHandler(socketserver.BaseRequestHandler):

    def init(self,packer=Packer.MessagePacker,parser=Parser.MessageParser):
        self.__packer = packer
        self.__parser = parser


    def putMessage(self,body=object,kind=Packer.MessageKind):    
        self.__packer.packingMessage(body,kind)

    def getMessage(self,kind=Packer.MessageKind):
        if kind == Packer.MessageKind.GAME:
            return self.__parser.getGameMessage()
        elif kind == Packer.MessageKind.GUI:
            return self.__parser.getGuiMessage()
        elif kind == Packer.MessageKind.NETWORK:
            return self.__parser.getNetworkMessage()
        else:
            print("not exist message kind")
            return False


    def handle(self):
        self.__setup()
        self.__requestPlayerInfo()
        
        while(True):
            self.__sendMessage()
            self.__recvMessage()         

        return super().handle()

    def getPakcer(self):
        return self.__packer

    def getParser(self):
        return self.__parser

    def __setup(self):
        
        str = "%s가 접속하였습니다" % (self.client_address[0] )
        gui.Watting.wattingThread.isConnect = True
        gui.Watting.ui.connectingEdit.setText(str);
        gui.Watting.ui.beginButton.setText("시작하기")  
        gui.Watting.ui.beginButton.setEnabled(True)
              
        return super().setup()


    def __sendMessage(self):
        data = self.__packer.getMessage()
        if type(data) != bool:
            self.request.send( pickle.dumps( data ))
            
    def __recvMessage(self):
        data = self.request.recv(1024)
        if len(data)<=0:
            return

        temp = pickle.loads(data) 
        self.__parser.loader(temp)
        
    def __requestPlayerInfo(self):
        playerInfo = Message.Message(Message.MessageKind.PLAYER_INFO)
        msg = Packer.Message(Packer.MessageKind.GAME,playerInfo)
        self.putMessage(msg,Packer.MessageKind.GAME)
        

class FroggerServer(threading.Thread):
    
    def init(self,ip,nickname):            

                

        self.serverIp = ip
        self.serverPort = PORT
        self.nickname = nickname

        tuple = (self.serverIp,self.serverPort)               
        self.tcpHandler = TCPHandler
        self.tcpHandler.init(self.tcpHandler,Packer.MessagePacker(),Parser.MessageParser())
        self.serverSocket = socketserver.TCPServer(tuple,self.tcpHandler)
        
    def run(self):
        self.serverSocket.serve_forever()
        self.tcpHandler.handle(self.tcpHandler)
        
    def putMessage(self,body=object,kind=Packer.MessageKind):    
        self.tcpHandler.putMessage(self.tcpHandler, body,kind)
    
    def getMessage(self,kind=Packer.MessageKind):
        return self.tcpHandler.getMessage( self.tcpHandler, kind)
    
    def getTCPHandler(self):
        return self.tcpHandler
 
    def resolveRequestedPlayerInfo(self):

        packer = self.tcpHandler.getPakcer(self.tcpHandler)

        while True:

            msg = self.getMessage(Packer.MessageKind.GAME)
            if type(msg) != bool:
                if msg.header == Message.MessageKind.PLAYER_INFO:
                    return msg.nickname
                else:
                    self.putMessage(msg,Packer.MessageKind.GAME)


def beginServerSocket(ip,nickname):
    server = FroggerServer()
    server.init(ip,nickname)
    server.start()
  
    return server
    
    
