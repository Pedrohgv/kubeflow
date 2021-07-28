import requests
import argparse
import zipfile
import os

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--gd_file_id', type=str, help='Google Drive file ID', required=True)
    parser.add_argument('--extracted_folder', type=str, help='Output that will contain extracted files')

    args = parser.parse_args()

    file_id = args.gd_file_id
    destination = args.extracted_folder

    print('Downloading file...')
    download_file_from_google_drive(file_id, 'file')

    print('Creating output folder...')
    os.makedirs(destination, exist_ok=True)

    print('Extracting file...')
    with zipfile.ZipFile('file',"r") as zip_ref:
        zip_ref.extractall(destination)