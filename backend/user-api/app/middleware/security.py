import bcrypt


def hash_password(password: str) -> str:
    """ Uses Bcrypt to hash user account password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, password: str) -> bool:
    """ Verifies plaintext password against bcrypt hashed password """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        password.encode('utf-8')
    )