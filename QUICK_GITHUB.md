# Publication GitHub - Aide-Mémoire Rapide

## Installation de Git (si nécessaire)

```bash
# openSUSE
sudo zypper install git

# Ubuntu/Debian
sudo apt install git
```

## Configuration initiale (une seule fois)

```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"
```

## Publication en 5 étapes

### 1. Initialiser Git

```bash
cd /home/pascal/github/conso-chauffage
git init
```

### 2. Premier commit

```bash
git add .
git commit -m "Initial commit: Application de suivi de chaudière"
```

### 3. Créer le dépôt sur GitHub

Allez sur https://github.com → New repository → `conso-chauffage`

⚠️ NE PAS cocher "Initialize with README"

### 4. Connecter et pousser

```bash
# Remplacez VOTRE_USERNAME par votre nom d'utilisateur GitHub
git remote add origin https://github.com/VOTRE_USERNAME/conso-chauffage.git
git branch -M main
git push -u origin main
```

### 5. C'est fait ! 🎉

Votre projet est maintenant sur GitHub : https://github.com/VOTRE_USERNAME/conso-chauffage

## Mises à jour futures

```bash
git add .
git commit -m "Description des modifications"
git push
```

## ⚠️ Important : Données personnelles

Si vous ne voulez PAS publier vos vraies données de consommation :

```bash
# Option 1 : Renommer vos données et créer un exemple
mv data/saisons.yaml data/saisons_perso.yaml
# Puis créer un fichier saisons.yaml avec des données d'exemple

# Option 2 : Ignorer complètement le fichier de données
echo "data/saisons.yaml" >> .gitignore
git rm --cached data/saisons.yaml
```

---

📖 **Guide complet** : Voir `PUBLICATION_GITHUB.md`
