import secrets
import string
import sys

def generate_secret(length=64):
    """Generates a secure, high-entropy string suitable for API keys or JWT secrets."""
    alphabet = string.ascii_letters + string.digits + "-_!@#"
    return ''.join(secrets.choice(alphabet) for i in range(length))

if __name__ == "__main__":
    length = 64
    if len(sys.argv) > 1:
        try:
            length = int(sys.argv[1])
        except ValueError:
            pass
            
    print(f"🔒 Generating {length}-char secure secret...\n")
    secret = generate_secret(length)
    print(f"Key: {secret}")
    print("\n(Copied to clipboard suggestions: No... wait, I'm a script.)")
