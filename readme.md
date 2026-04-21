
gcloud config set account <email address> <br>
gcloud auth login <br>
gcloud projects list <br>
gcloud config set project ccpa-394520 <br>
gcloud config set run/region us-west1 <br>
<!--Deploy current directory with settings set from above commands-->
gcloud run deploy --source .


**local SQLite DB Migration**

**If you want to start from scratch:**
Delete the migrations folder: rm -rf migrations/
(Optional but recommended) Drop all tables in your database for a completely clean slate.

in terminal
Run: export FLASK_APP=main.py
Run: flask db init
Run: flask db migrate -m "Initial migration"
Run: flask db upgrade

#Cloud sql proxy
gcloud auth application-default login
cloud-sql-proxy --unix-socket /cloudsql future-489121:us-west1:flaskdb




export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"