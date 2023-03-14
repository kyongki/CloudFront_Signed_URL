#!/bin/python3 
"""
pip3 install cryptography 
"""
import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from botocore.signers import CloudFrontSigner

# define variables
keyfile = 'cf-signed.pem'
key_id = 'K3QDKQM2M2Y6AQ' # get id from CloudFront Public keys' ID on AWS Console
#url = 'https://dpmmtkd00joye.cloudfront.net/secured_file.txt'
url = 'https://d3qzu5xbn874f2.cloudfront.net/secured_file.txt'
expire_year = 2023
expire_month = 3
expire_day = 15

def rsa_signer(message):
    with open(keyfile, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())

expire_date = datetime.datetime(expire_year, expire_month, expire_day)
print("ex: ", expire_date)

cloudfront_signer = CloudFrontSigner(key_id, rsa_signer)

# Create a signed url that will be valid until the specific expiry date
# provided using a canned policy.
signed_url = cloudfront_signer.generate_presigned_url(
    url, date_less_than=expire_date)
print(signed_url)
