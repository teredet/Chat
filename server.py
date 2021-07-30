from twisted.internet import reactor
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import ServerFactory, connectionDone

class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'

    def connectionMade(self):
        self.factory.clients.append(self)

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def lineReceived(self, line: bytes):
        content = line.decode()
        content = f"Message from USER: {content}"


        for user in self.factory.clients:
            user.sendLine(content.encode())

class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    
    def startFactory(self):
        self.clients = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()