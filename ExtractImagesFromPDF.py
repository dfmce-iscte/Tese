import os
import fitz  # PyMuPDF library
from tqdm import tqdm  # tqdm library for progress tracking

# Specify the directory containing PDF files
workdir = "RandomisedSample"

# Dictionary to store image counts per PDF
image_counts = {}

# Loop through each file in the directory
for each_path in os.listdir(workdir):
    if each_path.endswith(".pdf"):  # Check if the file is a PDF
        pdf_name = each_path[:-4]  # Remove ".pdf" extension

        # Create a directory for the PDF's images
        pdf_image_dir = os.path.join(workdir, pdf_name)
        os.makedirs(pdf_image_dir, exist_ok=True)

        doc = fitz.Document(os.path.join(workdir, each_path))  # Open the PDF document

        image_count = 0  # Counter for extracted images

        for i in range(doc.page_count):
            page = doc.load_page(i)
            for image in page.get_images():
                img = doc.extract_image(image[0])
                image_ext = img["ext"]
                image_data = img["image"]
                with open(os.path.join(pdf_image_dir, "p%s-%s.jpeg" % (i, image[0])), 'wb') as f:
                    f.write(image_data)
                image_count += 1
            break


        # # Loop through each page of the PDF
        # for i in tqdm(range(len(doc)), desc="pages"):
        #     # Loop through each image on the page
        #     for img in tqdm(doc.get_page_images(i), desc="page_images"):
        #         xref = img[0]  # Get the image reference
        #         image = doc.extract_image(xref)  # Extract the image data
        #         pix = fitz.Pixmap(doc, xref)  # Create a pixmap from the image reference
        #
        #         # Save the pixmap as a PNG image within the PDF's directory
        #         png_filename = os.path.join(pdf_image_dir, "p%s-%s.jpeg" % (i, xref))
        #         pix.save(png_filename)
        #
        #         image_count += 1
        #         pix = None  # Release the pixmap

        image_counts[pdf_name] = image_count

# Print the image counts for each PDF
for pdf_name, count in image_counts.items():
    print("Extracted %d pictures from %s.pdf" % (count, pdf_name))
