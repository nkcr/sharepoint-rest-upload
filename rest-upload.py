import json
import adal
import requests
import os
import sys
from uuid import uuid4

'''This script uploads a file to a sharepoint entry.
Authentication is made with a certificate.
Usage:
  python3 rest-upload <file path>

REST reference: https://docs.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-folders-and-files-with-rest
                https://msdn.microsoft.com/en-us/library/office/dn450841.aspx
Requests reference: http://docs.python-requests.org/en/master/user/advanced/
The 250MB restriction: https://blogs.technet.microsoft.com/sharepointdevelopersupport/2016/11/23/always-use-file-chunking-to-upload-files-250-mb-to-sharepoint-online/
Explanation and limitations: https://github.com/SharePoint/PnP/tree/dev/Samples/Core.LargeFileUpload#large-file-handling---option-3-startupload-continueupload-and-finishupload
'''

sharepoint_name = "peragus"
doc_path        = "Documents%20partages/Feedback%20louange" # Remote file path
chunck_size     = int(8e+6)

application_id = "bfb9d790-e3a4-465e-ae54-bc873d1bde27"  # from azure
tenant_id      = "58983bb8-f643-45dc-9926-36fe9b8e3b5b"  # (eebule)
authentication_uri = 'https://login.microsoftonline.com' # aka Authority
resource       = 'https://bullenetwork.sharepoint.com'
authority_url  = (authentication_uri + '/' + tenant_id)
certificate_path = "certificate/server.pem"

#
# Check arguments
# Read file path in argument
# Set file_name and file_path
# Check file size
#
if len(sys.argv) < 2:
  raise Exception("ERROR:", "Please provide file path in argument.")
file_path = os.path.abspath(sys.argv[1])
if os.path.exists(file_path):
  file_name = os.path.basename(file_path)
  file_size = os.path.getsize(file_path)
else:
  raise Exception("ERROR:", "File not found ({})".format(file_path))

#
# Method to read a file in chuncks
#
def read_chuncks(file, file_size, chunck_size=chunck_size):
  is_first, is_last = True, False
  tot_read = 0
  while not is_last:
    data = file.read(chunck_size)
    tot_read = tot_read + len(data)
    if tot_read == file_size:
      is_last = True
    yield data, is_first, is_last
    is_first = False

#
# Get the authentication token using certificate
# (accessing sharepoint won't work using secret key)
#
context = adal.AuthenticationContext(authority_url)
token = context.acquire_token_with_client_certificate(
        resource,                                   # The resource is sharepoint
        application_id,                             # From azure panel
        open(certificate_path, 'r').read(),         # Secret key
        "5B6EEFE90DDC3D7A73E055BDB15597462552DB9F") # Secret key fingerprint
access_token = str(token.get("accessToken"))

#
# Build the REST requests
# The first part is for simple /add
# The second part is for chunks
#
base_request = resource + "/sites/" + sharepoint_name + \
    "/_api/Web/GetFolderByServerRelativeUrl('{}')".format(doc_path)
request_get  = base_request + "/Files"
request_post = base_request + \
    "/Files/add(url='{}', overwrite=true)".format(file_name)
# Second part
base_chunk_request = resource + "/sites/" + sharepoint_name + \
    "/_api/Web/getfilebyserverrelativeurl('/sites/{}/{}/{}')".format(
        sharepoint_name, doc_path, file_name)
request_start_upload    = base_chunk_request + \
    "/startupload(uploadId=guid'{:s}')"
request_continue_upload = base_chunk_request + \
    "/continueupload(uploadId=guid'{:s}',fileOffset={:n})"
request_finish_upload   = base_chunk_request + \
    "/finishupload(uploadId=guid'{:s}',fileOffset={:n})"
request_cancel_upload   = base_chunk_request + \
    "/cancelupload(uploadId=guid'{:s}')"

#
# Make the call based on the request and header
#
with requests.Session() as s:
  # Sessions parameters
  s.headers.update({
    'Authorization': 'BEARER ' + access_token,
    "accept": "application/json;odata=verbose",
    "content-type": "application/json;odata=verbose",
    })

  offset = 0
  uuid = str(uuid4())

  # We catch any exception to ensure the transaction is finished proprely. Leaving
  # an unfinished transaction will lock the file 15 minutes and is removed after
  # few hours.
  try:
    # Creates an empty file
    # With chuncks upload, one has first to create an empty file and then use
    # `StarUpload`, `ContinueUpload`, and `FinishUpload` to update the empty file.
    s.headers.update({"content-length": "0"})
    r = s.post(request_post, data="")
    print("Uploading {} to {}".format(file_path, doc_path))
  
    for chunck, is_first, is_last in read_chuncks(open(file_path, 'rb'), file_size):
      s.headers.update({"content-length": str(len(chunck))})
      if is_first:
        r = s.post(request_start_upload.format(uuid), data=chunck)
        if is_last:
          # If there is only one chunck we directly end the transfer
          s.headers.update({"content-length": "0"})
          r = s.post(request_finish_upload.format(uuid, len(chunck)), data="")
      elif is_last:
        r = s.post(request_finish_upload.format(uuid, offset), data=chunck)
      else:
        r = s.post(request_continue_upload.format(uuid, offset), data=chunck)
      offset = offset + len(chunck)

      if r.status_code != 200:
        #print(json.dumps(r.json(), indent=2))
        raise Exception("ERROR:", r.status_code, r.text)
      else:
        print("Uploaded {}/{} bytes ({}%)".format(offset, file_size, 
                                                  int(offset/file_size*100)))
  except requests.exceptions.RequestException as e:
    r = s.post(request_cancel_upload.format(uuid))
    print(e)
    exit(1)

  result = r.json().get("d")
  print("Done! Uploaded {} bytes to {}".format(
      result["Length"], result["ServerRelativeUrl"]))
