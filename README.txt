Aadarsh Shikshan Sansthan - Flask School Website (Simple Dynamic Version)
--------------------------------------------------------
What's included:
- Flask app with Admin login (default: admin / admin123)
- Admin can add notices, results, view admissions, upload gallery images.
- Student can view results by roll number.
- Admission form saves to database.
- SQLite database (school.db) included.

How to run locally (Linux / Mac / Windows with WSL recommended):
1. Install Python 3.8+
2. Create virtualenv:
   python -m venv venv
   source venv/bin/activate   (Windows: venv\Scripts\activate)
3. Install requirements:
   pip install -r requirements.txt
4. Run:
   python app.py
5. Open http://127.0.0.1:5000 in your browser.

Default admin credentials:
  username: admin
  password: admin123

Deployment:
- You can deploy this to Render, Replit, or any other free Flask host.
- For Render, create a Web Service, connect repo, set start command: `python app.py`
