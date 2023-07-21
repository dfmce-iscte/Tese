import PyPDF2, re

# def extract_content(pdf_path):
#     with open(pdf_path, 'rb') as pdf:
#         pdf = PyPDF2.PdfFileReader(pdf)
#         for i in range(0, pdf.getNumPages()):

#
# def find_urls(text):
#     regex = r"(https?://\S+)"
#     all_url = re.findall(regex, text)
#     for url in all_url:
#         print(f"AN URL WAS FOUND: {url}")
#     return all_url
#
#
# def find_emails(text):
#     regex = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-z]+)"
#     all_emails = re.findall(regex, text)
#     for email in all_emails:
#         print(f"AN EMAIL WAS FOUND: {email}")
#     return all_emails
#
#
# email_text = "Please contact us at contact@tutorialspoint.com for further information." + \
#              " You can also give feedbacl at feedback@tp.com"
#
# url_text = "url para ser encontrado https://www.tutorialspoint.com/extract-hyperlinks-from-pdf-in-python"
#
# find_emails(email_text)
#
# find_urls(url_text)


pdf_reader = PyPDF2.PdfReader(open("Scotland/24_ Fête des Lumières Festival mobile app.pdf", "rb"))
count = 0

for page in pdf_reader.pages:
    for image in page.images:
        with open(image.name.split(".")[0] + str(count) + ".png", 'wb') as fp:
            fp.write(image.data)
            count += 1


# import imghdr
#
# image_type = imghdr.what("Image4940.png")
#
# if image_type:
#     print("The image can be loaded")
# else:
#     print("The image cannot be loaded")