import os
import fitz  # PyMuPDF library
from PIL import Image

from tqdm import tqdm  # tqdm library for progress tracking

# Specify the directory containing PDF files
# workdir = "RandomisedSample"


# Dictionary to store image counts per PDF
# image_counts = {}


def convert_jpx_to_jpeg(jpx_path, jpeg_path):
    with Image.open(jpx_path) as jpx_img:
        # Convert and save as JPG
        jpx_img.save(jpeg_path, 'JPEG')
    os.remove(jpx_path)


def get_pixels_width_height(img_path):
    with Image.open(img_path) as img_open:
        # Get the pixels
        pixels = list(img_open.getdata())

    return pixels


def is_image_almost_black(pixels):
    number_of_pixels = len(pixels)
    black_pixeis = 0
    for pixel in pixels:
        r, g, b = pixel
        if (r + g + b) / 765 < 0.1:
            black_pixeis += 1

    return black_pixeis / number_of_pixels > 0.55


# Extract images from PDF and returns the directory containing the images
def extract_images_from_pdf(pdf_path):
    pdf_name = pdf_path.split("/")[2][:-4]  # Remove ".pdf" extension

    # Create a directory for the PDF's images
    pdf_image_dir = os.path.join(pdf_path[:-4])
    # pdf_image_dir = workdir
    os.makedirs(pdf_image_dir, exist_ok=True)

    doc = fitz.Document(pdf_path)  # Open the PDF document

    image_count = 0  # Counter for extracted images

    for i in range(len(doc)):
        for image in doc.get_page_images(i):
            img = doc.extract_image(image[0])
            image_ext = img["ext"]
            image_data = img["image"]
            image_path = os.path.join(pdf_image_dir, f"{pdf_name}_{image_count}.{image_ext}")
            with open(image_path, 'wb') as f:
                f.write(image_data)
            image_count += 1

            if image_ext == "jpx":
                new_img_path = image_path.replace("jpx", "jpg")
                convert_jpx_to_jpeg(image_path, new_img_path)
                image_path = new_img_path

            if is_image_almost_black(get_pixels_width_height(image_path)):
                with open('images_to_fix.txt', 'a+') as f:
                    f.write(image_path + "\n")

    # print("Extracted %d pictures from %s.pdf" % (image_count, pdf_name))
    return pdf_image_dir

# # Loop through each file in the directory
# for each_path in os.listdir(workdir):
#     if each_path.endswith(".pdf"):  # Check if the file is a PDF
#         extract_images_from_pdf(each_path)
#
# # Print the image counts for each PDF
# for pdf_name, count in image_counts.items():
#     print("Extracted %d pictures from %s.pdf" % (count, pdf_name))
