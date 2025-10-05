import uvicorn
from cryptography.fernet import Fernet

if __name__ == "__main__":
    key = Fernet.generate_key()
    print(key)
    # uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=False)
