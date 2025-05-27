import hashlib
from urllib.parse import urlencode
 
# Set your variables here
email = "neko@nekonik.com"
default = "https://www.example.com/default.jpg"
size = 40
 
# Encode the email to lowercase and then to bytes
email_encoded = email.lower().encode('utf-8')
 
# Generate the SHA256 hash of the email
email_hash = hashlib.sha256(email_encoded).hexdigest()
 
# Construct the URL with encoded query parameters
query_params = urlencode({'d': default, 's': str(size)})
gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?{query_params}"
 
print(gravatar_url)
