#!/bin/bash

openssl genrsa -out key.pem 1024
openssl req -new -key key.pem -out request.pem
# self signed
openssl x509 -req -in request.pem -signkey key.pem -out cert.pem
