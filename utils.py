from passlib.context import CryptContext

# Adding 'bcrypt__ident="2b"' is the "magic" fix for this Windows ValueError
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b")

def hash(password: str):
    # We add a check to make sure the password isn't somehow empty
    if not password:
        return None
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

    