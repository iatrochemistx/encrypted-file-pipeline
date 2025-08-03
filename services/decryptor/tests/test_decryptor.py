from app.services.decryptor import decrypt_file

def test_decrypt_file_stub():
    result = decrypt_file("abc123")
    assert result == {"status": "ok", "file_id": "abc123"}
