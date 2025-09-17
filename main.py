from database import DatabaseConnection
from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    db = DatabaseConnection()
    db.close()