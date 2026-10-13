# ColoHouse

Plateforme de logement étudiant et de colocation.

- `backend/` : API REST et pages web — Django 5.1, Django REST Framework, PostgreSQL + PostGIS
- `mobile/` : application Flutter (en cours)

---

## Lancer le projet sur une nouvelle machine

Les commandes ci-dessous sont pour **Ubuntu / Debian**.

### 1. Installer les prérequis

| Outil | Version |
|---|---|
| Python | 3.12 ou 3.13 (Django 5.1 ne supporte pas 3.14) |
| PostgreSQL | 14 ou plus récent |
| PostGIS | extension PostgreSQL |
| GDAL / GEOS | bibliothèques géographiques utilisées par Django |
| Git | — |

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip \
                    postgresql postgresql-contrib postgis \
                    gdal-bin libgdal-dev libgeos-dev
```

Vérifier :

```bash
python3 --version      # 3.12 ou 3.13
psql --version         # 14+
gdalinfo --version     # doit afficher une version de GDAL
```

### 2. Récupérer le code

```bash
git clone <URL_DU_DEPOT> colohouse
cd colohouse/backend
```

### 3. Créer la base de données

```bash
sudo -u postgres psql -c "CREATE USER colohouse WITH PASSWORD 'colohouse' SUPERUSER;"
sudo -u postgres psql -c "CREATE DATABASE colohouse OWNER colohouse;"
```

Vérifier que la connexion fonctionne (mot de passe : `colohouse`) :

```bash
psql -h localhost -U colohouse -d colohouse -c "SELECT 1;"
```

### 4. Installer les dépendances Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements/dev.txt
```

### 5. Configurer l'environnement

```bash
cp .env.example .env
```

Puis générer une clé secrète et la coller dans `.env` à la place de `change-moi` :

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Contenu attendu de `backend/.env` :

```
DJANGO_SECRET_KEY=<la clé générée>
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgis://colohouse:colohouse@localhost:5432/colohouse
```

> Si tu as choisi un autre utilisateur / mot de passe / nom de base à l'étape 3,
> adapte `DATABASE_URL` : `postgis://UTILISATEUR:MOT_DE_PASSE@localhost:5432/BASE`

### 6. Créer les tables et un administrateur

```bash
python manage.py check          # → System check identified no issues
python manage.py migrate
python manage.py createsuperuser
```

### 7. Lancer le serveur

```bash
python manage.py runserver
```

Ouvrir **http://127.0.0.1:8000/**

| Page | URL |
|---|---|
| Site | http://127.0.0.1:8000/ |
| Annonces | http://127.0.0.1:8000/annonces/ |
| Administration | http://127.0.0.1:8000/admin/ |
| Documentation de l'API | http://127.0.0.1:8000/api/docs/ |

Pour que le filtre « Près du campus » fonctionne, ajouter au moins un campus
dans l'administration (`/admin/` → Campuses).

---

## Les fois suivantes

```bash
cd colohouse/backend
source .venv/bin/activate
python manage.py runserver
```

Après un `git pull` qui modifie les modèles ou les dépendances :

```bash
pip install -r requirements/dev.txt
python manage.py migrate
```
