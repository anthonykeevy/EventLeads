import os
print("DATABASE_URL:", os.getenv('DATABASE_URL', 'NOT SET'))
print("JWT_SECRET:", os.getenv('JWT_SECRET', 'NOT SET'))
print("CORS_ORIGINS:", os.getenv('CORS_ORIGINS', 'NOT SET'))


