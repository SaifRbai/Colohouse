# ColoHouse

Plateforme de logement étudiant et de colocation.

- `backend/` : API REST et pages web — Django 5.1, Django REST Framework, PostgreSQL + PostGIS
- `mobile/` : application Flutter (en cours)

---

## Lancer le projet sur une nouvelle machine

Les commandes ci-dessous sont pour **Ubuntu / Debian** (recommandé).
Pour Windows, voir la [note en bas de page](#windows).

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

---

## Problèmes fréquents

| Erreur | Solution |
|---|---|
| `password authentication failed for user "colohouse"` | L'utilisateur PostgreSQL n'existe pas ou le mot de passe diffère : refaire l'étape 3, ou corriger `DATABASE_URL` dans `.env`. |
| `Could not find the GDAL library` | GDAL n'est pas installé : `sudo apt install gdal-bin libgdal-dev`. |
| `could not open extension control file ".../postgis.control"` | PostGIS n'est pas installé : `sudo apt install postgis`. |
| `ImproperlyConfigured: Set the DJANGO_SECRET_KEY environment variable` | Le fichier `backend/.env` est absent : refaire l'étape 5. |
| `No module named 'django'` | L'environnement virtuel n'est pas activé : `source .venv/bin/activate`. |
| `Connection refused` sur le port 5432 | PostgreSQL est arrêté : `sudo systemctl start postgresql`. |
| `That port is already in use` | Un serveur tourne déjà ; sinon lancer sur un autre port : `python manage.py runserver 8001`. |

---

## Windows

GeoDjango (PostGIS + GDAL) est difficile à installer directement sous Windows.
La solution la plus simple est **WSL** (Ubuntu dans Windows) :

1. Dans PowerShell en administrateur : `wsl --install`, puis redémarrer.
2. Ouvrir « Ubuntu » depuis le menu Démarrer.
3. Suivre ce guide depuis l'étape 1, dans le terminal Ubuntu.

Le site reste accessible depuis le navigateur Windows sur http://127.0.0.1:8000/.
