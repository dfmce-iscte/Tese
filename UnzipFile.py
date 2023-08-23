import sys

if sys.version_info >= (3, 6):
    import zipfile
else:
    import zipfile36 as zipfile

with zipfile.ZipFile('quivr-0.0.46.zip', 'r') as zip_ref:
    zip_ref.extractall("Quivr")
