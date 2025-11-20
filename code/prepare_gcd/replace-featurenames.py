import re
import csv

def parse_doc(doc_file):
    code_map = {}
    current_code = None
    current_desc = []
    previous_line = ""

    with open(doc_file, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()

            # Skip empty lines and attribute headers
            if not stripped or stripped.lower().startswith("attribute") or \
            previous_line.lower().startswith("attribute"):
                previous_line = stripped
                continue

            # Match lines like "A11 : some description"
            match = re.match(r'^\s*(A\d{2,3})\s*[:\-]?\s+(.*)', line)

            if match:
                # Save the last code-description pair
                if current_code:
                    code_map[current_code] = ' '.join(current_desc).strip()

                current_code, first_desc = match.groups()
                current_desc = [first_desc.strip()]
            elif current_code:
                # Line is a continuation of the previous description
                current_desc.append(stripped)

        # Add the last entry
        if current_code and current_desc:
            code_map[current_code] = ' '.join(current_desc).strip()
        previous_line = stripped

    return code_map

def translate_and_write_csv(data_file, doc_file, output_file):
    # Column headers as per the German credit dataset
    headers = [
        "Status of existing checking account", "Duration in month", "Credit history",
        "Purpose", "Credit amount", "Savings account/bonds", "Present employment since",
        "Installment rate in percentage of disposable income", "Personal status and sex",
        "Other debtors / guarantors", "Present residence since", "Property", "Age in years",
        "Other installment plans", "Housing", "Number of existing credits at this bank",
        "Job", "Number of people being liable to provide maintenance for", "Telephone",
        "foreign worker","granted"
    ]

    # Parse code-to-description map
    code_map = parse_doc(doc_file)
    code_map['A122'] = code_map['A122'].removeprefix('if not A121 : ')
    code_map['A123'] = code_map['A123'].removeprefix('if not A121/A122 : ').removesuffix(', not in attribute 6')
    #string.removeprefix(prefix_to_remove)
    
    print(code_map['A122'])
    print(code_map['A123'])


    # Read and translate german.data, write to CSV
    with open(data_file, 'r', encoding='utf-8') as data_f, \
         open(output_file, 'w', newline='', encoding='utf-8') as out_f:

        writer = csv.DictWriter(out_f, fieldnames=headers)
        writer.writeheader()

        for line in data_f:
            tokens = line.strip().split()

            if len(tokens) != len(headers):
                print(f"Skipping malformed line: {line.strip()}")
                continue

            translated = [code_map.get(token, token) for token in tokens]
            row = dict(zip(headers, translated))
            writer.writerow(row)

    print(f"✅ CSV translation complete. Output saved to: {output_file}")

# Example usage:
# translate_and_write_csv("german.data", "german.doc", "german_translated.csv")

if __name__ == "__main__":
    # Set file paths here
    data_file = "../../data/german-credit-dataset/statlog+german+credit+data/german.data"
    doc_file = "../../data/german-credit-dataset/statlog+german+credit+data/german.doc"
    output_file = "../../data/german-credit-dataset/gcd_values-decoded.csv"

    translate_and_write_csv(data_file, doc_file, output_file)
