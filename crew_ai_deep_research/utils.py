import os
from dotenv import load_dotenv, find_dotenv

def load_env():
    # find_dotenv() searches for the file starting in the current directory
    # and moving up the folder tree.
    dotenv_path = find_dotenv()
    if not dotenv_path:
        print("Warning: .env file not found!")
    load_dotenv(dotenv_path)

def get_openai_api_key():
    load_env()
    key = os.getenv("OPENAI_API_KEY")
    if key is None:
        raise ValueError("OPENAI_API_KEY not found. Check your .env file.")
    return key

def get_exa_api_key():
    load_env()
    key = os.getenv("EXA_API_KEY")
    if key is None:
        raise ValueError("EXA_API_KEY not found. Check your .env file.")
    return key