import codecs
import random
import re
import string
from datetime import datetime
from pathlib import Path


def generate_email(allow_invalid=False):
    domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com', 'example.com', 'mail.ru', 'yandex.ru', 'qq.com', '163.com', 'naver.com', 'daum.net', 'web.de', 'gmx.de', 'orange.fr', 'free.fr', 'libero.it', 'rambler.ru', 'protonmail.ch', 'rediffmail.com', 'hotmail.co.uk', 'yahoo.co.uk', 'yahoo.co.jp', 'yahoo.com.br', 'outlook.com.au', 'mail.yahoo.co.jp', 'googlemail.com', 'gmx.net', 't-online.de', 'sina.com.cn']
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 10)))
    domain = random.choice(domains)
    if allow_invalid and random.random() < 0.1:
        # Generate invalid email (missing @ or domain)
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 10)))
    return f"{username}@{domain}"

def generate_password(delimiter=None, allow_non_ascii=False):
    if delimiter and random.random() < 0.2:
        parts = [''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(4, 8))) for _ in range(2)]
        password = f"{parts[0]}{delimiter}{parts[1]}"
    else:
        # Remove problematic characters from string.punctuation
        safe_punctuation = ''.join(c for c in string.punctuation if c not in '"\n\r\t')
        password = ''.join(random.choices(string.ascii_letters + string.digits + safe_punctuation, k=random.randint(8, 16)))
    
    if allow_non_ascii and random.random() < 0.1:
        # Include some non-ASCII characters
        non_ascii = ''.join(chr(random.randint(128, 2000)) for _ in range(random.randint(1, 3)))
        password += non_ascii
    
    # Remove control characters (ASCII 0-31 and 127-159)
    password = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', password)
    password = password.replace('"', '').replace('\n', '').replace('\r', '').replace('\t', '')
    
    return password

def generate_mixed_encoding_file(file_path):
    with open(file_path, 'wb') as f:
        f.write("Line 1 in UTF-8\n".encode('utf-8'))
        f.write("Line 2 in UTF-16\n".encode('utf-16'))
        f.write("Line 3 in ISO-8859-1\n".encode('iso-8859-1'))

def generate_bom_file(file_path):
    with open(file_path, 'wb') as f:
        f.write(codecs.BOM_UTF8)
        f.write("File with BOM\n".encode('utf-8'))

def generate_mixed_line_endings(file_path):
    with open(file_path, 'wb') as f:
        f.write("Line with \\n\n".encode('utf-8'))
        f.write("Line with \\r\r".encode('utf-8'))
        f.write("Line with \\r\\n\r\n".encode('utf-8'))

def generate_no_line_endings(file_path):
    with open(file_path, 'wb') as f:
        f.write("Line1Line2Line3".encode('utf-8'))

def generate_file_content(delimiter, num_rows, add_comments=False, add_multiline_comment=False, allow_invalid=False, allow_non_ascii=False):
    content = []
    if add_multiline_comment:
        content.extend([
            "# This is a multiline comment\n",
            "# It spans multiple lines\n",
            "# And provides some context\n",
            "\n"
        ])
    for i in range(num_rows):
        password = generate_password(delimiter, allow_non_ascii)
        line = f"{generate_email(allow_invalid)}{delimiter}{password}"
        if add_comments and random.random() < 0.2:
            line += f" # This is a comment for line {i+1}"
        content.append(line + "\n")
    return ''.join(content)

def generate_random_url():
    protocols = ['http', 'https']
    tlds = ['.com', '.org', '.net', '.io', '.co', '.us', '.me']
    protocol = random.choice(protocols)
    domain = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
    tld = random.choice(tlds)
    path = '/'.join(''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8))) for _ in range(random.randint(1, 3)))
    return f"{protocol}://{domain}{tld}/{path}"

def generate_nfo_greetz():
    return f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                         GREETZ FROM                          ║
    ║                    THE CREDENTIAL DUMPERS                    ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  Shoutout to all our homies in the Telegram channel:         ║
    ║  t.me/CredDumpersUnite                                       ║
    ║                                                              ║
    ║  Keep it legal, keep it clean, and always hash your passes!  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """

def create_test_data():
    base_dir = Path("test_data") / f"test_{datetime.now().strftime('%Y%m%d')}"
    base_dir.mkdir(parents=True, exist_ok=True)

    delimiters = {
        "comma": ",",
        "semicolon": ";",
        "colon": ":",
        "mixture": [",", ";", ":", "|", "\t"]
    }

    for subdir, delimiter in delimiters.items():
        subdir_path = base_dir / subdir
        subdir_path.mkdir(exist_ok=True)

        for i in range(5):
            filename = f"file_{i+1}.txt"
            file_path = subdir_path / filename
            
            if subdir == "mixture":
                current_delimiter = random.choice(delimiter)
            else:
                current_delimiter = delimiter

            add_comments = (i == 2)
            add_multiline_comment = (i == 4)

            content = generate_file_content(current_delimiter, 100, add_comments, add_multiline_comment, allow_invalid=True, allow_non_ascii=True)
            
            with open(file_path, 'w') as f:
                f.write(content)

    errors_dir = base_dir / "errors"
    errors_dir.mkdir(exist_ok=True)

    url_file_path = errors_dir / "random_url.txt"
    with open(url_file_path, 'w') as f:
        f.write(generate_random_url())

    nfo_file_path = errors_dir / "greetz.nfo"
    with open(nfo_file_path, 'w') as f:
        f.write(generate_nfo_greetz())

    special_cases_dir = base_dir / "special_cases"
    special_cases_dir.mkdir(exist_ok=True)

    for encoding in ['utf-8', 'utf-16', 'iso-8859-1']:
        file_path = special_cases_dir / f"{encoding}_file.txt"
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(generate_file_content(',', 10, allow_invalid=True, allow_non_ascii=True))


    generate_mixed_encoding_file(special_cases_dir / "mixed_encoding.txt")
    generate_bom_file(special_cases_dir / "bom_file.txt")
    generate_mixed_line_endings(special_cases_dir / "mixed_line_endings.txt")
    generate_no_line_endings(special_cases_dir / "no_line_endings.txt")

    print(f"Test data generated in {base_dir}")

if __name__ == "__main__":
    create_test_data()
