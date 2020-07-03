import pdfplumber
import re
import pandas as pd
import glob
from collections import namedtuple

# heeaders for csv
Line = namedtuple('Line', 'sport_id order_date order_ref_number item_description item_category item_size qty_ordered item_size_chart item_unit item_pref_vendor item_manuf item_manuf_model item_price item_serial item_expendable item_universal')

# identifying patterns in text using regular expressions
manuf_model_re = re.compile(r'^(\w+) (.*) \d+ \$(\d+\.?\d+) \$\d+\.?\d+ \D+')

# main logic for going through the pdf and extracting specific text
lines = []

for file in glob.iglob("put_pdfs_here/*pdf"):
    with pdfplumber.open(file) as pdf:
        pages = pdf.pages
        for page in pdf.pages:
            text = page.extract_text()
            text_lines = text.split("\n")
            for i in range(len(text_lines)):
                
                # regular expressions - used for identifying patterns in text
                model_num = manuf_model_re.search(text_lines[i])
                
                # Order Date
                if text_lines[i].startswith('Order Date'):
                    order_date = re.compile(r'(\d{2}/\d{2}/\d{4})').search(text_lines[i]).group(1)
                
                # Order Reference Number
                elif text_lines[i].startswith('Customer PO#:'):
                    ref_num = re.compile(r'Customer PO#:(.*) Contact').search(text_lines[i]).group(1)
                
                # Manufacture Model
                elif model_num:
                    manuf_model = model_num.group(1)
                    item_description = model_num.group(2)
                    price = model_num.group(3)
                    
                # Sizes
                elif text_lines[i].startswith('Size'):
                    item_description += ' '+text_lines[i - 1]
                    sizes = re.compile(r'Size (.*)').search(text_lines[i]).group(1).split()
                    qtys = re.compile(r'Qty (.*)').search(text_lines[i + 1]).group(1).split()
                    for i in range(len(qtys)):
                        lines.append(Line("", order_date, ref_num, item_description, "", sizes[i], qtys[i], "", "Each", "", "Adidas", manuf_model, price, "N", "Y", "N"))

# constructing a dataframe and outputting to a csv
df = pd.DataFrame(lines)
df.to_csv('formatted.csv', index=False)



