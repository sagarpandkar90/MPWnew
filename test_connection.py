import bcrypt
from db_config import get_connection

conn = get_connection()
cur = conn.cursor()

# Fetch users who still have plain passwords
cur.execute("SELECT id, password_hash FROM users")
rows = cur.fetchall()

for user_id, plain_pass in rows:
    # Skip already-hashed passwords
    if plain_pass and plain_pass.startswith("$2b$"):
        continue

    # Hash only plain-text passwords
    hashed = bcrypt.hashpw(plain_pass[:72].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, user_id))
    print(f"✅ Hashed password for user id: {user_id}")

conn.commit()
cur.close()
conn.close()
print("All plain-text passwords converted to bcrypt hashes ✅")

