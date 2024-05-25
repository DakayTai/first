import sys
import requests

# Ambil url dari argumen baris perintah
url = sys.argv[1]

# Lakukan permintaan ke situs web
response = requests.get(url)

# Tampilkan HTTP status code
print("HTTP Status Code:", response.status_code)

# Tampilkan header
print("Headers:")
for header, value in response.headers.items():
    print(header + ": " + value)
