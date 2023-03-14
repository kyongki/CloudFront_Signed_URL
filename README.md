# CloudFront_Signed_URL
This document explains how to configure CloudFront to support signed URL. You can configure CloudFront to require that users access your files using either signed URLs or Cookies. This feature will help you restrict access to files in CloudFront caches.

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

## Create basic distribution of CloudFront
Create distribution in CloudFront Console
![create distribution](/images/img-1.png)



## Prepare keys and script
### create private and public key
### create the script which print out the signed url
## Verify signed URL

