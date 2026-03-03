python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt

python manage.py makemigrations siteapp
python manage.py migrate
python manage.py load_data

python manage.py runserver