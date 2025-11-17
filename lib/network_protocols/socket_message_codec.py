'''

def decode(message: bytes) -> MessageFormat:
    return message.decode("utf-8")

def encode(message: MessageFormat) -> bytes:
    return message.encode("utf-8")

    
'''
