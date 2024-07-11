import time

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException
import pandas as pd
import json

url = 'https://www.nestportugal.pt/portfolio'
options = webdriver.EdgeOptions()
options.add_argument('--headless')
driver = webdriver.Edge(options=options)
# driver = webdriver.Edge()
driver.maximize_window()

driver.get(url)
driver.execute_script("window['last_article_name'] = '';")
print("Page loaded")

name_col, logo_col, email_col, phone_col, link_col, description_col, bussines_col, filters_col = \
    ('Name', 'Logo', 'Email', 'Phone', 'Link', 'Description', 'Business Type', 'Filters')
df = pd.DataFrame(
    columns=[name_col, logo_col, email_col, phone_col, link_col, description_col, bussines_col, filters_col])
delimiter = "------------------------"
old_description = ""
output_equal_descriptions = ""


def analyse_page():
    global old_description, output_equal_descriptions
    filter_bar = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'filterbar')))
    articles = filter_bar.find_elements(By.CSS_SELECTOR, 'article')

    for index, article in enumerate(articles):
        new_row = {}
        name = article.find_element(By.CLASS_NAME, 'name').get_attribute('textContent')
        new_row[name_col] = name
        print("\t", name)

        article_front = article.find_element(By.CLASS_NAME, 'article-front')
        logo = article_front.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
        new_row[logo_col] = logo

        article_back = article.find_element(By.CLASS_NAME, 'article-back')
        contacts = article_back.find_elements(By.CSS_SELECTOR, 'a')
        for contact in contacts:
            href = contact.get_attribute('href')
            if href.startswith('mailto:'):
                new_row[email_col] = href.split(':')[1]
            elif href.startswith('tel:'):
                new_row[phone_col] = href.split(':')[1]
            elif href.startswith('http'):
                new_row[link_col] = href

        more_about_script = open("MoreAboutScript.js", "r").read()
        name = name.replace('"', '\\"')
        more_about_script += f'\nget_more_about({index}, "{name}", arguments[arguments.length - 1]);'
        description = driver.execute_async_script(more_about_script)
        new_row[description_col] = description
        if description == old_description:
            print(f"{delimiter}\n\tSolution has the same description as the previous one\n{delimiter}")
            output_equal_descriptions += f"Current: {name}; Previous: {df.iloc[-1][name_col]}\n"
        old_description = description

        new_row[bussines_col] = article.get_attribute('data-businessfilter')
        new_row[filters_col] = article.get_attribute('data-filter').replace('-', ' | ')
        # print(json.dumps(new_row, indent=1))
        df.loc[len(df)] = new_row

    # print(f"Total articles: {len(articles)}")


def new_iteration(iteration):
    global ignore_pages, boundary
    if ignore_pages and iteration < boundary:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'filterbar')))
    else:
        analyse_page()
    next_page_script = open("NextPage.js", "r").read()
    next_page_script += '\nnextPage(arguments[arguments.length - 1]);'
    driver.execute_async_script(next_page_script)


def save_df_to_excel():
    # df.to_excel('Portfolio1.xlsx', index=False)
    writer = pd.ExcelWriter('Portfolio.xlsx', engine='xlsxwriter')
    df.to_excel(writer, index=False)

    # Get the xlsxwriter workbook and worksheet objects
    worksheet = writer.sheets['Sheet1']

    # Iterate through each of the URLs and write them as hyperlinks
    for row, _ in enumerate(df['Logo']):
        logo_url = df[logo_col][row]
        if pd.notna(logo_url):
            worksheet.write_url(row + 1, 1, str(logo_url), string='here')
        link = df[link_col][row]
        if pd.notna(link):
            worksheet.write_url(row + 1, 4, str(link), string='site')

    writer.close()

    open("EqualDescriptions.txt", "a", encoding='utf-8').write(output_equal_descriptions)


def extract(total_pages_or_boundary):
    new_iteration(1)

    paginaWrapper = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'paginaWrapper')))
    paginaWrapper_options = paginaWrapper.find_elements(By.CSS_SELECTOR, 'small')
    total_pages = int(paginaWrapper_options[-1].get_attribute('textContent'))
    print(f"{delimiter}\nTotal number of pages to scrap: {total_pages}\n{delimiter}")

    final_page = total_pages + 1 if total_pages_or_boundary else boundary

    for i in range(2, final_page):
        print("\nPage ", i)
        new_iteration(i)


try:
    print("\nPage ", 1)
    ignore_pages = False
    boundary = 24

    extract(ignore_pages)
    driver.get(url)
    ignore_pages = True
    extract(ignore_pages)

    print(f"{delimiter}\nTotal dataframe rows: {len(df)}\n{delimiter}")

    driver.quit()
except (TimeoutException, NoSuchElementException, JavascriptException) as e:
    print(f"Error: {e}")
    time.sleep(1000)

save_df_to_excel()
