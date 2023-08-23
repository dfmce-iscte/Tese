import zipfile

with zipfile.ZipFile('/home/dcosme/quivr-0.0.46.zip', 'r') as zip_ref:
    zip_ref.extractall('/home/dcosme')
