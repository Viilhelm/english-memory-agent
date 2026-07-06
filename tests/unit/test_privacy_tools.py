from english_memory_agent.tools.privacy_tools import privacy_scan


def test_privacy_scan_safe():
    res = privacy_scan("I went to school yesterday to meet my teacher.")
    assert res["safe_to_save"] is True
    assert len(res["risks"]) == 0

def test_privacy_scan_email():
    res = privacy_scan("Please send the details to user@example.com.")
    assert res["safe_to_save"] is False
    assert any("email" in r for r in res["risks"])

def test_privacy_scan_phone():
    res = privacy_scan("You can call me at +1-555-829-1002.")
    assert res["safe_to_save"] is False
    assert any("phone" in r for r in res["risks"])

def test_privacy_scan_password():
    res = privacy_scan("My password = mysecretpass123")
    assert res["safe_to_save"] is False
    assert any("password" in r for r in res["risks"])
    
    res = privacy_scan("Set your token: 'abcd1234efgh5678'")
    assert res["safe_to_save"] is False
    assert any("password" in r for r in res["risks"])

def test_privacy_scan_id_numbers():
    # SSN
    res = privacy_scan("SSN: 000-12-3456")
    assert res["safe_to_save"] is False
    assert any("SSN" in r for r in res["risks"])
    
    # Credit Card
    res = privacy_scan("Card number is 4111-1111-1111-1111")
    assert res["safe_to_save"] is False
    assert any("Credit Card" in r for r in res["risks"])
    
    # Chinese National ID
    res = privacy_scan("ID number: 110101199003072340")
    assert res["safe_to_save"] is False
    assert any("ID card" in r for r in res["risks"])

def test_privacy_scan_address():
    # English Address
    res = privacy_scan("Meet me at 123 Baker Street, London.")
    assert res["safe_to_save"] is False
    assert any("address" in r for r in res["risks"])
    
    # Chinese Address
    res = privacy_scan("地址在北京市朝阳区建国路88号。")
    assert res["safe_to_save"] is False
    assert any("address" in r for r in res["risks"])
