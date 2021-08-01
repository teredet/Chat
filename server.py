from twisted.internet import reactor
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import ServerFactory, connectionDone

class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def connectionMade(self):
        self.send_login_notification()
        self.factory.clients.append(self)

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def is_login_taken(self, login: str):
        is_taken = False
        for user in self.factory.clients:
            if user.login == login: 
                is_taken = True
                break
        return is_taken

    def store_history(self, message: str):
        if len(self.factory.last_messages) == 10:
            self.factory.last_messages.pop(0)
        self.factory.last_messages.append(message)
    
    def send_history(self):
        for message in self.factory.last_messages:
            self.sendLine(message.encode())

    def send_login_notification(self):
        if len(self.factory.clients) > 0:
            self.sendLine("Already exists:".encode())
            for user in self.factory.clients:
                self.sendLine(user.login.encode())
            self.sendLine("".encode())
        self.sendLine("Log in using the folowing form \"login:NAME\"".encode())

    def login_user(self, content: str):
        if content.startswith("login:"):
            user_login = content.replace("login:", "")
            if not self.is_login_taken(user_login):
                self.login = user_login
                self.sendLine("Welcome!".encode())
                self.send_history()
                for user in self.factory.clients:
                    if user != self and user.login != None:
                        user.sendLine(f"{self.login} conected.".encode()) 
            elif self.is_login_taken(user_login):
                self.sendLine(f"Login \"{user_login}\" is already in use.".encode())
                return
        else:
            self.sendLine("Invalid login. Log in using the folowing form: \"login:NAME\"".encode())
            return

    def lineReceived(self, line: bytes):
        content = line.decode()
        if self.login is not None:
            content = f"{self.login}: {content}"
            self.store_history(content)
            for user in self.factory.clients:
                if user.login != None:
                    user.sendLine(content.encode())        
        elif self.login is None:
            self.login_user(content)


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    last_messages: list
    
    def startFactory(self):
        self.clients = []
        self.last_messages = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()
