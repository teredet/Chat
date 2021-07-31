from twisted.internet import reactor
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import ServerFactory, connectionDone

class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None
    logins: list

    def connectionMade(self):
        self.factory.clients.append(self)

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def lineReceived(self, line: bytes):
        content = line.decode()

        if self.login is not None:
            content = f"Message from {self.login}: {content}"

            for user in self.factory.clients:
                if user is not self:
                    user.sendLine(content.encode())
        
        elif self.login is None:
            if content.startswith("login:"):
                user_login = content.replace("login:", "")
                
                if user_login not in self.logins:
                    self.login = user_login
                    self.logins.append(user_login)
                    self.sendLine("Welcome!".encode())

                elif user_login in self.logins:
                    self.sendLine(f"Login {user_login} is already in use.".encode())

            else:
                self.sendLine("Invalid login".encode())


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    
    def startFactory(self):
        self.clients = []
        self.protocol.logins = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()