import bcrypt

def verify_password(plain_password, hashed_password):
    if not hashed_password:
        return False
    # bcrypt.checkpw expects bytes
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        # hashed_password might be stored as string, but checkpw needs bytes
        hashed_password = hashed_password.encode('utf-8')
    
    try:
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password):
    if isinstance(password, str):
        password = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    # Return as string (for database storage)
    return hashed.decode('utf-8')
