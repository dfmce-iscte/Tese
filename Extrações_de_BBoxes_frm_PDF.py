# -----------------------------------------------
# create a preview of the images with the bounding box overlaid
from PIL import Image, ImageDraw


def preview_images_with_box(image_files, box):
    for image_file in image_files:
        image = Image.open(image_file)
        draw = ImageDraw.Draw(image)
        draw.rectangle(box, outline='red', width=3)
        image.show()


# -----------------------------------------------
# extract Images from PDF to folder
from pdf2image import convert_from_path


def pdf_to_images(input_pdf, output_dir):
    images = convert_from_path(input_pdf, poppler_path=r"venv\poppler-23.07.0\Library\bin")
    for i, image in enumerate(images):
        image.save(f'{output_dir}/page_{i}.png', 'PNG')


# -----------------------------------------------
# extract box from Images from PDF and compile new PDF: This does not specify the pdf output page size
from PIL import Image
from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter


def extract_box(input_pdf, output_pdf, box):
    with open(output_pdf, 'wb') as output_file:
        writer = PdfWriter()
        images = convert_from_path(input_pdf, poppler_path=r"venv\poppler-23.07.0\Library\bin")
        for i, image in enumerate(images):
            cropped_image = image.crop(box)
            cropped_image.save(f'temp_{i}.pdf')
            with open(f'temp_{i}.pdf', 'rb') as temp_file:
                writer.add_page(PdfReader(temp_file).pages[0])
        writer.write(output_file)


# -----------------------------------------------
# extract box from Images from PDF and compile new PDF: This specifies the pdf output page size --> in this case A4
from PyPDF2 import PdfReader, PdfWriter, PageObject, Transformation
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import tempfile
import os


def extract_box_pageSize(input_pdf, output_pdf, box):
    with open(output_pdf, 'wb') as output_file:
        writer = PdfWriter()
        images = convert_from_path(input_pdf, poppler_path=r"venv\poppler-23.07.0\Library\bin")
        for i, image in enumerate(images):
            cropped_image = image.crop(box)
            temp_file_fd, temp_file_path = tempfile.mkstemp(suffix='.pdf')
            try:
                cropped_image.save(temp_file_path)
                page = PageObject.create_blank_page(None, *A4)
                page2 = PdfReader(temp_file_path).pages[0]
                scale = min(A4[0] / float(page2.mediabox.width), A4[1] / float(page2.mediabox.height))
                page2.add_transformation(Transformation().scale(scale).translate(0, 0))
                page.merge_page(page2)
                writer.add_page(page)
            finally:
                os.close(temp_file_fd)
                os.remove(temp_file_path)

        writer.write(output_file)


if __name__ == '__main__':
    # -----------------------------------------------
    #  create a preview of the images with the bounding box overlaid --> preview_images_with_box(image_files, box)
    # image_file = ['YourImageHere']
    # preview_images_with_box(image_file, (180, 200, 1500, 2000))
    # -----------------------------------------------
    #  extract box from Images from PDF and compile new PDF (with no page size deffined)
    # extract_box('C:\\Users\\amg13\\Downloads\\sapotransfer-600e96e81feaea6\\05-Capitulos 11 e 12.pdf', 'output_BBoxPDF.pdf', (180, 200, 1500, 2000))
    # -----------------------------------------------    
    #  extract box from Images from PDF and compile new PDF (with A4 page size deffined)
    extract_box_pageSize('YourPDFHere', 'Your_output_PDFHere', (180, 200, 1500, 2000))
    # -----------------------------------------------
    #  extract Images from PDF to folder
    # pdf_to_images('YourPDFHere', 'YourOutputFolderHere')
