# Student Outing Management System

A simple Flask-based web application to manage student outings. Users can **register**, **log in**, start outings with reasons, mark returns, and view outing history. All timestamps are stored in **IST (Asia/Kolkata)** timezone.

---

## Features

- **Student Registration & Login**  
- **Start & Mark Return for Outings**  
- **View Current Outing Status**  
- **View Outing History**  
- **Timezone-aware timestamps (IST)**  

---

## Tech Stack

- **Backend:** Python 3.x, Flask  
- **Database:** MySQL  
- **Timezone Handling:** `pytz`  
- **Deployment:** Vercel-compatible  

---

## Requirements

Python packages:
Flask==2.3.3
Werkzeug==2.3.3
mysql-connector-python==8.1.1
pytz==2025.2

---
## Notes

- All times are stored and displayed in Asia/Kolkata timezone.

- Passwords are securely hashed using Werkzeug.

- Only logged-in students can access their outing pages.
