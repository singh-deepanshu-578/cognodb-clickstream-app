import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            os.getenv("COGNODB_URI"),
            auth=(os.getenv("COGNODB_USER"), os.getenv("COGNODB_PASSWORD")),
        )
    return _driver

def close_driver():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None