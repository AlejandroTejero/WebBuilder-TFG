Para poder escoger un LLM personalizado debemos meter la api key, pero guardarla tal cual en la base de datos no es lo mejor, para ello se cifrara con django-encrypted-model-fields.

Para cifrar necesitarás instalar django-encrypted-model-fields:
bashpip install django-encrypted-model-fields

Y añadir en settings.py una clave de cifrado (añádela también al .env):
python# settings.py
FIELD_ENCRYPTION_KEY = os.getenv("FIELD_ENCRYPTION_KEY", "")

Para generar la clave ejecuta esto una sola vez en tu terminal y copia el resultado al .env:
bashpython -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

En el .env añade:
FIELD_ENCRYPTION_KEY=tu_clave_generada_aqui

Una vez hecho eso, dime y añadimos el modelo UserProfile a tu models.py