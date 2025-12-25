# How to Publish CitizenConnect for Free

I recommend using **Render.com**. It is free, connects to GitHub, and supports Python applications perfectly.

## Step 1: Push to GitHub
You need to push your code to a new GitHub repository.
1. Create a new repo on [GitHub.com](https://github.com/new). Name it `citizen-connect`.
2. Run these commands in your terminal (I have already initialized git for you):
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/citizen-connect.git
   git branch -M main
   git push -u origin main
   ```

## Step 2: Create Database (Free Postgres)
Render's free database lasts only 90 days. For permanent free storage, use **Neon.tech**.

1.  **Sign Up**: Go to [Neon.tech](https://neon.tech) and sign up (you can use your GitHub account).
2.  **Create Project**: 
    -   Click **"New Project"**.
    -   Name it `citizen-connect-db`.
    -   Choose a Region close to you (e.g., Singapore for India).
    -   Database Name: `neondb` (default is fine).
    -   Click **"Create Project"**.
3.  **Get Connection String**:
    -   You will be redirected to the **Dashboard**.
    -   Look for the **"Connection Details"** section on the right or center.
    -   Ensure **"Postgres"** is selected in the dropdown.
    -   **Important**: Copy the connection string. It starts with `postgres://` or `postgresql://`.
    -   *Example*: `postgres://kishore:AbCdEf123@ep-cool-frog-123456.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`
    -   Save this string! You will need it for Step 3.

## Step 3: Deploy App on Render
1. Go to [Render.com](https://render.com) and Sign Up.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. **Settings**:
   - **Name**: `citizen-connect`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables** (Advanced):
   Add these keys and values from your `.env` file (Use the *Values*, not the encrypted strings, wait!):
   
   **IMPORTANT**: In Production (Render), we typically do NOT use the Fernet encryption for environment variables because Render ENCRYPTS them for you in their dashboard.
   
   However, your code (`security_utils.py`) expects them to be encrypted tokens if they are marked as secrets.
   
   **Simplest Path**:
   - Set `ENCRYPTION_KEY` in Render (Copy from your local `.env`).
   - Set `SMTP_USER`, `SMTP_PASSWORD`, `ADMIN_USERNAME` using the **Encrypted Strings** (starting with `gAAAA...`) from your local `.env`.
   - Set `DATABASE_URL` (From Neon).
     - **Note**: Paste the entire connection string starting with `postgres://...` you copied from Neon.tech here.
   - Set `GOOGLE_API_KEY` (Plain text).
   - Set `ADMIN_PASSWORD_HASH` (Copy the `$2b$...` hash).

6. Click **Deploy**.

Your website will be live at `https://citizen-connect.onrender.com`!
