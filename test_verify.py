from werkzeug.security import check_password_hash

password = "12345678"
hash = "pbkdf2:sha256:260000$vsdwOkxwo7J050Xz$29b860036996b187ea5be7f33b9a6a6f2e5f7ab911ed1f1d0d3e581502dc0a4c"

print("Result:", check_password_hash(hash, password))
