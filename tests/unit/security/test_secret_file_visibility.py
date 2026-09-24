from pathlib import Path

from harness.security.secret_file_visibility import SecretFileVisibility


def test_secret_file_visibility_hides_sensitive_files():
    visibility = SecretFileVisibility()
    
    assert not visibility.is_visible(Path(".env"))
    assert not visibility.is_visible(Path(".env.local"))
    assert not visibility.is_visible(Path("secret.pem"))
    assert not visibility.is_visible(Path("private.key"))
    assert not visibility.is_visible(Path("config/.env"))
    assert not visibility.is_visible(Path("keys/server.pem"))
    assert visibility.is_visible(Path("main.py"))