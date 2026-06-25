from app.core.security import create_access_token, hash_password, verify_password


def test_password_hash_and_verify():
    hashed = hash_password("kaiops-secure")
    assert verify_password("kaiops-secure", hashed)


def test_access_token_creation():
    token = create_access_token(subject="user-1", tenant_id="tenant-1", roles=["admin"])
    assert isinstance(token, str)
    assert len(token) > 20
