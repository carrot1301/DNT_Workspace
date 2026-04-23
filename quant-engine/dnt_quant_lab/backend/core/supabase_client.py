import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

def get_supabase() -> Client:
    """
    Returns a configured Supabase client using the service role key.
    This gives the backend admin privileges to update balances.
    """
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise ValueError("Supabase credentials are not set in the environment variables.")
    
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
