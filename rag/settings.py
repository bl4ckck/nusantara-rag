import os


def get(key):
    if not os.getenv(key) and os.path.exists(".env"):
        for line in open(".env", encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"missing required env var: {key}")
    return value
