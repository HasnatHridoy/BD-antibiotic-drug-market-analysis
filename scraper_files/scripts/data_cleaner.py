import pandas as pd
import re



def process_data(data_extract):
    """
    Processes raw scraped data and returns a clean pandas DataFrame.
    """

    def extract_price(text):
        match = re.search(r'৳\s*([\d,.]+)', text)
        return float(match.group(1).replace(',', '')) if match else None

    def extract_strip_price(text):
        match = re.search(r'\([^)]*৳\s*([\d,.]+)\)', text)
        return float(match.group(1).replace(',', '')) if match else None

    def extract_pack_size(text):
        match = re.search(r'\((\d+\s*x\s*\d+)', text)
        if match:
            return match.group(1).strip() + " pcs"
        match = re.search(r"(\d+\s*[a-zA-Z/%']+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def extract_pack_type(text):
        match = re.search(r'\b(bottle|tube|sachet|vial|ampoule|refill|pack|drop)\b', text, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        if re.search(r'\d+\s*x\s*\d+', text):
            return "strip"

    def add_processed_fields(data):
        processed = []
        for row in data:
            pack_price_text = row[5]
            price = extract_price(pack_price_text)
            strip_price = extract_strip_price(pack_price_text)
            pack_size = extract_pack_size(pack_price_text)
            pack_type = extract_pack_type(pack_price_text)
            processed.append(row + [price, strip_price, pack_size, pack_type])
        return processed

    # Expand multiple price entries per row
    expanded_data = []
    for item in data_extract:
        regular_info = item[:5]
        pack_price_str = item[5]
        if '\n' in pack_price_str:
            for entry in pack_price_str.split('\n'):
                expanded_data.append(regular_info + [entry])
        else:
            expanded_data.append(item)

    # Process and create DataFrame
    final_data = add_processed_fields(expanded_data)
    column_names = ['generics', 'product_name', 'dosage_form', 'strength', 'company',
                    'ref_p&p', 'unit_price', 'strip_price', 'pack_size', 'pack_type']
    df = pd.DataFrame(final_data, columns=column_names)
    df = df.drop('ref_p&p', axis=1)

    return df
