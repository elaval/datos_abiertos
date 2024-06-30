# data_utils/data_processing.py

import os
import pandas as pd
import requests
from zipfile import ZipFile
import chardet

def download_file(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download file from {url}")

def detect_encoding(file_path, num_bytes=1000):
    with open(file_path, 'rb') as f:
        raw_data = f.read(num_bytes)
    result = chardet.detect(raw_data)
    return result['encoding']

def read_csv_file(file_path, delimiter=';', header='infer', names=None):
    encoding = detect_encoding(file_path)
    print(f"Detected encoding for {file_path}: {encoding}")
    try:
        df = pd.read_csv(file_path, sep=delimiter, encoding=encoding, index_col=False, low_memory=False, header=header, names=names)
        print(f"Successfully read file with encoding {encoding}")
        return df
    except Exception as e:
        print(f"Error reading CSV file {file_path}: {e}")
        return None

def extract_csv_from_zip(zip_path, extract_filename, delimiter=';', header='infer', names=None):
    with ZipFile(zip_path, 'r') as zip_file:
        if extract_filename in zip_file.namelist():
            with zip_file.open(extract_filename) as f:
                # Save the file temporarily to detect encoding
                temp_csv_path = os.path.join("/tmp", extract_filename)
                with open(temp_csv_path, 'wb') as temp_f:
                    temp_f.write(f.read())
                df = read_csv_file(temp_csv_path, delimiter=delimiter, header=header, names=names)
                return df
        else:
            print(f"{extract_filename} not found in the zip archive.")
            return None

def process_zip_file(url, extract_filename, source_dir, processed_dir, delimiter=';', header='infer', names=None):
    # Extract filename from URL
    zip_filename = url.split('/')[-1]
    zip_path = os.path.join(source_dir, zip_filename)

    # Check if the file already exists
    if not os.path.exists(zip_path):
        # Download the zip file if it doesn't exist
        download_file(url, zip_path)
        print(f"Downloaded {zip_filename}")
    else:
        print(f"{zip_filename} already exists. Skipping download.")
    
    # Extract and process the CSV file
    df = extract_csv_from_zip(zip_path, extract_filename, delimiter=delimiter, header=header, names=names)
    if df is not None:
        parquet_filename = extract_filename.replace('.csv', '.parquet')
        parquet_path = os.path.join(processed_dir, parquet_filename)
        df.to_parquet(parquet_path)
        print(f"Processed {extract_filename} and saved to {parquet_path}")

