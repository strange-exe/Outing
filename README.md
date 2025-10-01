# Student Outing Management System

## Project Description

The **Student Outing Management System** is a web-based application built with Flask and MySQL designed to streamline the management of student outings in hostels or institutions.  
It allows students to **register**, **log in**, **start outings**, **mark returns**, and **view their outing history**. The application ensures accurate tracking by storing timestamps in the **Asia/Kolkata (IST) timezone**, making it suitable for Indian institutions or campuses.  

The system also emphasizes **security** by hashing passwords with Werkzeug and restricting access to authenticated users only.

---

## Demo Link
[Click Here](https://outing.abhinesh.me/)

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

**Python packages:**

- Flask==2.3.3
- Werkzeug==2.3.3
- mysql-connector-python==8.1.1
- pytz==2025.2

---
## Notes

- All times are stored and displayed in Asia/Kolkata timezone.

- Passwords are securely hashed using Werkzeug.

- Only logged-in students can access their outing pages.
