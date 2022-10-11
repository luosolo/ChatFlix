

class Guest:
    """
    This class encode the guest in the chat, you can change your name
    
    """
    def __init__(self, name, address, socket) -> None:
        self.name = name
        self.address = address
        self.socket = socket
        
        


    def say(self, message):
        return f"{self.name} says: {message}"

    def __repr__(self) -> str:
        return f"<Guest: name:{self.name} address:{self.address}>"