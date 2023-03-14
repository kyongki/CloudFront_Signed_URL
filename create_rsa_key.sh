#!/bin/sh
#
PRIVATE_KEY="cf-signed.pem"
PUB_KEY="cf-signed.pub"
openssl genrsa -out $PRIVATE_KEY 2048
echo "private key is created"

openssl rsa -pubout -in $PRIVATE_KEY -out $PUB_KEY
echo "public key is created"
