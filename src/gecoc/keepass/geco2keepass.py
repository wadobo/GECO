#!/usr/bin/env python

import sys
import datetime
import getpass
from pykeepass import PyKeePass
from pykeepass.kdbx_parsing.kdbx import KDBX
import slowaes
import hashlib


def strip(cad):
    index = cad.find(chr(0))
    to_ret = cad[0:index] if index > 0 else cad
    return to_ret


class CustomAES:
    def __init__(self):
        self.aes = slowaes.AESModeOfOperation()

    def encrypt(self, msg, key):
        ckey, iv = self.key_and_iv(key)
        mode, orig_len, ciph = self.aes.encrypt(msg, self.aes.modeOfOperation["CBC"],
                ckey, self.aes.aes.keySize["SIZE_128"], iv)
        return '#'.join(map(str, ciph))

    def decrypt(self, msg, key):
        msg = list(map(int, msg.split('#')))
        ckey, iv = self.key_and_iv(key)
        decr = self.aes.decrypt(msg, 256, self.aes.modeOfOperation["CBC"], ckey,
                self.aes.aes.keySize["SIZE_128"], iv)
        return strip(decr)

    def key_and_iv(self, key):
        '''
        Return a 32 size number key and a 16 size iv from a string key
        '''
        hkey = hashlib.sha256(key.encode()).digest()
        iv = hashlib.md5(key.encode()).digest()

        return hkey, iv


if len(sys.argv) < 2:
    print("Modo de empleo: {} <input.geco>")
    sys.exit()

input_file = sys.argv[1]
output_file = 'db.kdbx'
master = getpass.getpass("Contraseña maestra: ")

aes = CustomAES()
kp = PyKeePass('database.kdbx', password="liufhre86ewoiwejmrcu8owe")
kp.password = master

groups = {}

with open(input_file, 'r') as f:
    for p in f.readlines():
        name, type, description, account, password, cypher_method, updated, expiration = p.split("|")
        expiration = datetime.datetime.fromtimestamp(float(expiration))
        updated = datetime.datetime.fromtimestamp(float(updated))
        name, type, description, account =\
                map(lambda x: x.replace("\\n", "\n"), (name, type, description, account))

        clear = aes.decrypt(password, master)

        if type and not type in groups:
            group = kp.add_group(kp.root_group, type)
            groups[type] = group
        group = groups.get(type, kp.root_group)

        kp.add_entry(group, name, account, clear, notes=description)
    kp.save(output_file)
