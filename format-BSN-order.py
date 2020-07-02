import pdfplumber
import re
import pandas as pd
import glob
from collections import namedtuple

# headers for csv
Line = namedtuple('Line', 'sport_id order_date order_ref_number item_description item_category item_size qty_ordered chart item_unit item_pref_vendor item_manuf item_manuf_model item_price item_serial item_expendable item_universal')

# identifying patterns in text using regular expressions
manuf_model_re = re.compile(r'Item # - (.*)')
quantities_re = re.compile(r'\s*(\d*) ([A-Z]{2})\D*(\d*\.?\d*)')

# main logic for going through the pdf and extracting specific text
lines = []
check_info = False
check_sizes = False

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
                elif text_lines[i].startswith('Cart Name'):
                    ref_num = re.compile(r'Cart Name:(.*)').search(text_lines[i]).group(1)
                
                # Manufacture Model
                elif model_num:
                    item_description = text_lines[i - 2]
                    manuf_model = model_num.group(1)
                    # check text_lines[i + 2] to see if there are sizes for current item
                    if bool(quantities_re.search(text_lines[i + 2])) or text_lines[i + 1].startswith('Subtotal'):
                        info = quantities_re.search(text_lines[i - 1])
                        qty = info.group(1)
                        item_unit = "Each" if info.group(2) == "EA" else "Pair"
                        price = info.group(3)
                        lines.append(Line("", order_date, ref_num, item_description, "", "", qty, "", item_unit, "", "BSN", manuf_model, price, "N", "Y", "N"))
                    else:
                        check_sizes = True
                    
                # Sizes
                elif check_sizes:
                    sizes = text_lines[i].split()
                    info = quantities_re.search(text_lines[i - 2])
                    qty = info.group(1)
                    item_unit = "Each" if info.group(2) == "EA" else "Pair"
                    price = info.group(3)
                    qtys = re.findall(r'\d+', text_lines[i + 1])
                    for i in range(len(qtys)):
                        lines.append(Line("", order_date, ref_num, item_description, "", sizes[i], qtys[i], "", item_unit, "", "BSN", manuf_model, price, "N", "Y", "N"))
                    check_sizes = False
                    

# constructing a dataframe and outputting to a csv
df = pd.DataFrame(lines)
df.to_csv('formatted.csv', index=False)



