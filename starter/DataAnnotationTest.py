import requests
from bs4 import BeautifulSoup
import pandas as pd

# read in URL
url = 'https://docs.google.com/document/d/e/2PACX-1vRMx5YQlZNa3ra8dYYxmv-QIQ3YJe8tbI3kqcuC7lQiZm-CSEznKfN_HYNSpoXcZIV3Y_O3YoUB1ecq/pub'
# response = pd.read_html(url, encoding='Unicode')
response = requests.get(url)

# Try explicitly setting encoding
response.encoding = "utf-8"  # Try also "ISO-8859-1" if UTF-8 doesn't work
soup = BeautifulSoup(response.text, "html.parser")

# Extract table normally
table = soup.find("table")
headers = [th.text.strip() for th in table.find_all("th")]
rows = [[td.text.strip() for td in tr.find_all("td")] for tr in table.find_all("tr")[1:]]
df = pd.DataFrame(rows, columns=headers)

print(df)


# You may write helper functions, but there should be one function that:
# 1. Takes in one argument, which is a string containing the URL for the Google Doc with the input data, AND
# 2. When called, prints the grid of characters specified by the input data, displaying a graphic of correctly oriented uppercase letters.