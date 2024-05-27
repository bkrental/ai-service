from dotenv import load_dotenv
import os

def load_environment_variables():
    env = os.getenv('ENV', 'local')
    env_file = f".env.{env}"

    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        raise FileNotFoundError(f"{env_file} not found")

