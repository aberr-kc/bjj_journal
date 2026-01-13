@app.get("/debug-user/{username}")
def debug_user(username: str):
    from app.database import SessionLocal
    from app.models import User
    import hashlib
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return {"error": "User not found"}
        
        # Test passwords
        test_passwords = ["test", "password", "abarr", "123456"]
        results = {}
        
        for pwd in test_passwords:
            sha256_hash = hashlib.sha256(pwd.encode()).hexdigest()
            results[pwd] = {
                "sha256_matches": sha256_hash == user.hashed_password,
                "sha256_hash": sha256_hash
            }
        
        return {
            "username": username,
            "stored_hash": user.hashed_password,
            "hash_type": "bcrypt" if user.hashed_password.startswith("$2b$") else "sha256",
            "test_results": results
        }
    finally:
        db.close()