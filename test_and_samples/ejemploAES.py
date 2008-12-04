from Crypto.Cipher import AES
import base64

def multiplo(cad, length=16):
    n = len(cad)
    n = length - (n % length)
    return cad + chr(0)*n

def cifrar(cad, password):
    c = AES.new(multiplo(password))
    cifrado = c.encrypt(multiplo(cad))
    return base64.b64encode(cifrado)

def descifrar(cad, password):
    c = AES.new(multiplo(password))
    cad = base64.b64decode(cad)
    descifrado = c.decrypt(cad)
    return strip(descifrado)

def strip(cad):
    index = cad.find(chr(0))
    to_ret = cad[0:index] if index > 0 else cad
    return to_ret
