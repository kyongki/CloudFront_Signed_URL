# CloudFront_Signed_URL
This document explains how to configure CloudFront to support signed URL. You can configure CloudFront to require that users access your files using either signed URLs or Cookies. This feature will help you restrict access to files in CloudFront caches.

for more detail, refer to aws doc: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-signed-urls.html 

## Architecture
![architecture](/images/archi.png)

-----
## Work through
- requirement
- create basic distribution
- prepare keys and gen-signed-url script
- verify signed url

## Requirements
- aws cli
- python3
  - boto3, cryptography

install requried library
``` shell
pip3 install boto3 cryptography
```

## Basic CloudFront distribution
### create CloudFront distribution
Create distribution in CloudFront Console.
![create distribution](/images/img-1.png)

Select S3 bucket.
![select bucket](/images/img-2.png)

Set Origin access.
![origin access](/images/img-3.png)

Leave remains as default and click *Create distribution*.
![finish setting](/images/img-4.png)

Wait until *Last modified* changed from *Deploying* to time. It will take around 5 min.
![deploying](/images/img-5.png)
![deploying](/images/img-6.png)

### verify working of CloudFront
copy a file from local to s3 bucket with aws cli.
``` shell
aws s3 cp secured_file.txt s3://your-own-dest-seoul/
upload: ./secured_file.txt to s3://your-own-dest-seoul/secured_file.txt
```

confirm cloudfront domain.
![cf domain](/images/img-7.png)

access *secured_file.txt* on web browser. It should show you the content of file.
![web browser](/images/img-8.png)

## Prepare keys and script
### create private and public key
create private key and public key with openssl tool.
file name is [create_rsa_key.sh](create_rsa_key.sh)
``` shell
cat create_rsa_key.sh

#!/bin/sh
#
PRIVATE_KEY="cf-signed.pem"
PUB_KEY="cf-signed.pub"
#
openssl genrsa -out $PRIVATE_KEY 2048
echo "private key is created"
#
openssl rsa -pubout -in $PRIVATE_KEY -out $PUB_KEY
echo "public key is created"
```

If you run above script, you will see 2files, cf-signed.pem and cf-signed.pub.
``` shell
sh create_rsa_key.sh 

Generating RSA private key, 2048 bit long modulus
.....................+++
................+++
e is 65537 (0x10001)
private key is created
writing RSA key
public key is created
```
### register public key into CloudFront
goto CloudFront Console and click *Public Keys* menu
![cf-public_keys_menu](/images/img-9.png)

create public key in CloudFront console
![cf-public_keys](/images/img-10.png)

paste the content of public key file.
``` shell
$ cat cf-signed.pub
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAn4gfJlCgFbx9QVu14W/X
5NHH72SJFskfuQswF0Dp3LqueAbeliZ0ghh1MJdzdkcVcSz2YtSlE9IZf4HMtwjg
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxXxXxXx
/4ZSC9Ci7KBmJd0EzumRKOLaCx1XPlk5gYyK1w18CXmyAXDI3IN//DSmZbA69/mr
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxXxXxXx
BcNP8/0382KhliaisMpkocIUOqBIVgfpMxOt7WVpGlgRCAbJ5F4Zj8TQl3+nhvm5
cwIDAQAB
-----END PUBLIC KEY-----
```

confirm *public keys* is created and copy *key id*. This *key id* will be used in *gen_signed_url.py* script.
![cf-public_keys](/images/img-11.png)

create *key group* in AWS Console
![cf-public_keys](/images/img-12.png)

### create the script which print out the signed url
create python code to generate signed url.
file name is [gen_signed_url.py](gen_signed_url.py).
code is came from boto3 example(https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#generate-a-signed-url-for-amazon-cloudfront).
``` python
#!/bin/python3
"""
pip3 install cryptography
""" import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from botocore.signers import CloudFrontSigner

# define variables
keyfile = 'cf-signed.pem'
key_id = 'K3QDKQM2M2Y6AQ' # get id from CloudFront Public keys' ID on AWS Console
url = 'https://d6nc3lfreqo9p.cloudfront.net/secured_file.txt'
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
```

Change variables for your environment.
- keyfile: private key file name which you create.
- key_id: get id from CloudFront Public keys' ID on AWS Console
- url: CloudFront Distribution's domain name and file name
- expire_year/month/day: expiring date

run [gen_signed_url.py](gen_signed_url.py)
``` shell
$ python3 gen_signed_url.py
ex:  2023-03-15 00:00:00
https://d6nc3lfreqo9p.cloudfront.net/secured_file.txt?Expires=1678838400&Signature=esskzhkG8DO7Jbkjq6k7yYE0Lo7aSONj17u10P5t40Os~~XiEWUCK1CC4RRovXzWKrj4jsrINzRp9MzNrL8t50SowFVm2gMxaWbBhOU39BZ~Bz0Z1u73K9zX7Bt8b55Mft9vFqXQG~hyxhTaRrvEKzZpuj6dPMEL-at5ISbtPdebNx62O4BOLaevOrCRXEbBLPgIQpZSKsBZHXdnp6e6e4ZOvbITBErXwE7lBrdrpZuXWLjpdWMQGZlojIIkK0JTA460xMz5xjJ21tUwdc~MnqmLWCcTktC8KHfo-yY1A61VMwilqeIWy0AIvleRxqa0u0WO9tusp5gzwrOFRVwSaA__&Key-Pair-Id=KLD0H7IDXJ2MX
```
copy output url in notepad.

### Configure Distribution to support signed url
Select *Behaviors* and click *Edit*.
![cf-behaviors](/images/img-13.png)

Configure *restrict view access*.
![cf-restirct](/images/img-14.png)

Wait until *Last modified* from *Deploying* to real time.

## Verify signed URL
Confirm your previous access is denied.
![access-denied](/images/img-15.png)

Now, paste signed-url generated from *gen_signed_url.py*
![access-allowed](/images/img-16.png)

If you can see the content of file, your configuration works well

## Addtional Tips
When you modify the file, it will take some time to reflect the change in CloudFront. In this case, you can update the cache manually using *Invalidation*
![invalidation](/images/img-17.png)
