# JGPT Deployment & Security Guide

This guide explains how to access JGPT from your phone and secure it with your own credentials.

## 1. Remote Access (Phone)
Since JGPT runs on your computer (via Docker), your phone cannot reach `http://localhost:3000`. You need a "Tunnel" or a "Cloud Host".

### Option A: The "ngrok" Tunnel (Easiest / Free)
Use this to quickly check JGPT from your phone without setting up a server.
1.  **Install ngrok**: `brew install ngrok/ngrok/ngrok`
2.  **Start JGPT**: Ensure `make up` is running.
3.  **Start Tunnel**:
    ```bash
    ngrok http 3000
    ```
4.  **Visit Link**: ngrok will give you a URL (e.g., `https://random-name.ngrok-free.app`). Open this on your phone.
    *   *Note*: The API also needs to be accessible. You might need to tunnel port 8000 as well or configure ngrok configuration.

### Option B: Cloud Hosting (Recommended for Production)
Deploy the source code to a VPS (e.g., DigitalOcean, AWS Lightsail).
1.  Download `JGPT_Enterprise_Source_v1.0.zip` from your portal.
2.  Upload to the server.
3.  Run `make up`.
4.  Point your domain (e.g., `jgpt.yourcompany.com`) to the server IP.

---

## 2. Changing the Admin Password
By default, the system seeds `admin@jgpt.com` / `admin`. **You MUST change this.**

### Method 1: Python Script (Fastest)
I included a script `create_user_inner.py` in the source.

1.  **Edit the Script**:
    Open `products/JGPT/JGPTa/create_user_inner.py` and change line 11:
    ```python
    hashed = pwd_context.hash("YOUR_NEW_SECRET_PASSWORD")
    ```
    *(And optionally change the email on line 10/18)*.

2.  **Run the Script**:
    ```bash
    # Inside the Docker container (ensures dependencies exist)
    docker compose exec api python create_user_inner.py
    ```

### Method 2: Environment Variables
1.  Create a `.env` file in `products/JGPT/JGPTa` (copy `.env.example`).
2.  Set `SECRET_KEY` to a long random string. This invalidates all old tokens (logs everyone out).
    ```bash
    SECRET_KEY="super-long-random-string-that-only-you-know"
    ```
3.  Restart: `make up` (or `docker compose up -d --build`).

## 3. Creating a New Admin User
If you want a totally new user:
1.  Edit `create_user_inner.py`.
2.  Change `user@jgpt.com` to `yourname@company.com`.
3.  Change `role="user"` to `role="admin"`.
4.  Run the script inside Docker.
