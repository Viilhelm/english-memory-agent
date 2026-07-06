import re

def luhn_checksum(card_number: str) -> bool:
    try:
        digits = [int(c) for c in card_number]
    except ValueError:
        return False
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        doubled = d * 2
        checksum += doubled if doubled < 10 else doubled - 9
    return checksum % 10 == 0

def verify_cn_id(id_str: str) -> bool:
    if len(id_str) != 18:
        return False
    if not id_str[:17].isdigit():
        return False
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_digits = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    try:
        total = sum(int(id_str[i]) * weights[i] for i in range(17))
        return id_str[17].upper() == check_digits[total % 11]
    except Exception:
        return False

def privacy_scan(text: str) -> dict:
    """
    Scans the provided text for sensitive Personally Identifiable Information (PII)
    including email addresses, phone numbers, possible passwords/API keys,
    ID-like numbers, and home address-like text.
    
    Args:
        text (str): The string to scan.
        
    Returns:
        dict: A dict conforming to:
              {
                "safe_to_save": bool,
                "risks": list[str]
              }
    """
    if not text:
        return {"safe_to_save": True, "risks": []}
        
    risks = []
    
    # 1. Email detection
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    if re.search(email_pattern, text):
        risks.append("Detected potential email address.")
        
    # 2. Phone number detection
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    if re.search(phone_pattern, text):
        risks.append("Detected potential phone number.")
        
    # 3. Possible password/API key detection
    secrets_pattern = r'(?:api[-_]?key|password|secret|passwd|token|key)\s*[:=]\s*([\'"][a-zA-Z0-9_\-]+[\'"]|[a-zA-Z0-9_\-]{8,})'
    if re.search(secrets_pattern, text, re.IGNORECASE):
        risks.append("Detected possible password, API Key, or secret token.")
        
    # 4. ID-like numbers (SSN, credit card, or national ID number)
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    credit_card_pattern = r'\b(?:\d[ -]*?){13,16}\b'
    cn_id_pattern = r'\b\d{17}[\dXx]\b'
    
    if re.search(ssn_pattern, text):
        risks.append("Detected pattern resembling a Social Security Number (SSN).")
        
    cc_matches = re.finditer(credit_card_pattern, text)
    for match in cc_matches:
        cleaned = re.sub(r'[^\d]', '', match.group(0))
        if 13 <= len(cleaned) <= 16 and luhn_checksum(cleaned):
            risks.append("Detected pattern resembling a Credit Card number.")
            break
            
    cn_matches = re.finditer(cn_id_pattern, text)
    for match in cn_matches:
        cleaned = match.group(0)
        if verify_cn_id(cleaned):
            risks.append("Detected pattern resembling a National ID card number.")
            break
        
    # 5. Home address-like text detection
    # Common English address format: number + street name + street type suffix
    address_suffix = (
        r'\b(?i:street|st|avenue|ave|road|rd|highway|hwy|square|sq|trail|trl|'
        r'drive|dr|court|ct|parkway|pkwy|circle|cir|boulevard|blvd|lane|ln|'
        r'building|bldg|apartment|apt|room|rm)\b'
    )
    english_address_pattern = rf'\b\d+\s+(?:[A-Za-z0-9#-]+\s+){{1,4}}{address_suffix}'
    # Simple Chinese address character check
    chinese_address_pattern = r'[\u4e00-\u9fa5]+(?:省|市|区|县|路|街|号|弄|楼|室)'
    
    if re.search(english_address_pattern, text):
        risks.append("Detected pattern resembling a physical home address (English format).")
    elif re.search(chinese_address_pattern, text):
        risks.append("Detected pattern resembling a physical home address (Chinese format).")
        
    safe = len(risks) == 0
    return {
        "safe_to_save": safe,
        "risks": risks
    }
