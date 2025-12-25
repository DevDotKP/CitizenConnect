import os
from cryptography.fernet import Fernet

ENV_FILE = ".env"

def migrate_env():
    # 1. Generate Key or Read Existing
    key = None
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                if line.startswith("ENCRYPTION_KEY="):
                    key = line.strip().split("=", 1)[1]
                    break
    
    if not key:
        print("No ENCRYPTION_KEY found in .env, generating new one...")
        key = Fernet.generate_key().decode()
    
    cipher = Fernet(key.encode())
    
    # 2. Read existing Lines
    if not os.path.exists(ENV_FILE):
        print("No .env found")
        return

    with open(ENV_FILE, "r") as f:
        lines = f.readlines()

    new_lines = []
    has_key = False
    
    # Target Keys to Encrypt
    TARGETS = ["SMTP_USER", "SMTP_PASSWORD", "ADMIN_USERNAME", "GOOGLE_API_KEY"]
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            new_lines.append(line)
            continue
            
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            
            if k == "ENCRYPTION_KEY":
                has_key = True
                new_lines.append(f"{k}={v}")
                continue
                
            if k in TARGETS:
                # Encrypt if not already
                if not v.startswith("gAAAA"):
                    encrypted = cipher.encrypt(v.encode()).decode()
                    new_lines.append(f"{k}={encrypted}")
                    print(f"Encrypted {k}")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    if not has_key:
        new_lines.insert(0, f"ENCRYPTION_KEY={key}")
        print("Generated and added ENCRYPTION_KEY")

    # 3. Write Back
    with open(ENV_FILE, "w") as f:
        f.write("\n".join(new_lines) + "\n")
    
    print("Migration Complete.")

if __name__ == "__main__":
    migrate_env()
