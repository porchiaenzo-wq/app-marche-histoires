# Histoires de l'app de marche

Ce dépôt contient les histoires téléchargées par l'app. Chaque modification
envoyée sur la branche `main` est **vérifiée**, puis **publiée** sur
GitHub Pages ; l'app récupère la nouvelle version à sa prochaine ouverture
(au plus toutes les 6 heures), sans mise à jour de l'app.

## Ajouter ou modifier une histoire

1. Dans le dossier `histoires/`, ajoute un fichier `<id>.json` (par exemple
   `phare-perdu.json`) ou modifie un fichier existant. Le plus simple :
   copier une histoire existante et changer son contenu.
2. Ajoute l'identifiant dans `histoires/index.json`, à la place voulue
   (l'ordre de la liste est celui de la bibliothèque).
3. Valide (« Commit changes »). Dans l'onglet **Actions**, une coche verte
   veut dire que l'histoire est en ligne ; une croix rouge indique une
   erreur, expliquée en français dans le détail.

## Les règles vérifiées

- entre 5 et 10 chapitres, numérotés 1, 2, 3… ;
- chapitre 1 offert (`stepsRequired` : 0), les autres entre 3000 et 5000 pas ;
- chaque chapitre a un titre, un teaser, du texte et un souvenir ;
- un souvenir final par histoire ;
- les souvenirs ont un identifiant unique qui commence par l'id de
  l'histoire, et une icône connue de l'app (liste dans
  `outils/icones.json`) ;
- `genre` : `adventure`, `fantasy`, `crime`, `romance`, `horror` ou
  `scienceFiction`.

Pour vérifier sur un ordinateur : `python3 outils/verifier.py`.

## Ce qui est publié

`outils/construire_site.py` prépare `v1/catalogue.json` (liste des
histoires et leur « révision ») et `v1/histoires/<id>.json`. Les fichiers
sont publics : n'y mets rien de personnel.
