Uploads a file to sharepoint using the REST API and `adal` module for the
authentication using a certificate.

### Set up

```bash
$ virtualenv env # Creates a virtualenv in the env folder
$ source env/bin/activate # Load the virtualenv
$ pip3 install -r requirements.txt # Install dependencies
$ python3 rest-upload.py <file path> # Run the script
```

### Generate the certificate

From https://github.com/AzureAD/azure-activedirectory-library-for-python/wiki/Client-credentials

Generate a key:

`openssl genrsa -out server.pem 2048`

Create a certificate request:

`openssl req -new -key server.pem -out server.csr`

Generate a certificate:

`openssl x509 -req -days 365 -in server.csr -signkey server.pem -out server.crt`

You will have to upload this certificate (server.crt) on Azure Portal in your application settings. Once you save this certificate, the portal will give you the thumbprint of this certificate which is needed in the acquire token call. The key will be the server.pem key you generated in the first step.

### Create the app

Go to `https://portal.azure.com` and `Azure Active Directory` > `App Registration`. From there create an `Wep App / Api` application and on the app settings go to `Keys` and upload the `server.crt` file. Note the fingerprint.

The *Tenant_id* can be found from `Azure Active Directory` > `Properties`.

### Usage

```bash
$ python3 rest-upload <file path>
```

### Limitations

This script uses batch upload and has the only limitation of 30 minutes per upload.