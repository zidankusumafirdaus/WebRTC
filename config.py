import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask / JWT
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

    # Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_ATTACHMENTS_BUCKET = os.getenv('SUPABASE_ATTACHMENTS_BUCKET', 'attachments')
    SUPABASE_REPORTS_BUCKET = os.getenv('SUPABASE_REPORTS_BUCKET', 'reports')

    # Redis / Realtime
    REDIS_URL = os.getenv('REDIS_URL')
    REDIS_KEY = os.getenv('REDIS_KEY')

    # Attachment settings
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB'))
    ALLOWED_MIME_PREFIXES = [p.strip() for p in os.getenv('ALLOWED_MIME_PREFIXES').split(',') if p.strip()]
    ALLOWED_MIME_FULL = {p.strip() for p in os.getenv('ALLOWED_MIME_FULL').split(',') if p.strip()}
    REPORT_ALLOWED_MIME_FULL = {p.strip() for p in os.getenv('REPORT_ALLOWED_MIME_FULL', 'application/pdf,application/x-pdf,application/acrobat,application/vnd.pdf').split(',') if p.strip()}