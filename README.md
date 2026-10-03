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
  `scienceFiction` ;
- les personnages et lieux cités par les chapitres existent dans
  `univers.json`, avec des identifiants uniques.

## Le thème graphique (`themeId`)

Chaque histoire annonce son style : `retro-map` (carte d'explorateur,
aventure), `grimoire` (fantastique) ou `polar` (style moderne). Un nom
inconnu de l'app s'affiche avec le style moderne.

## Le multivers : personnages et lieux (`histoires/univers.json`)

Les personnages et les lieux sont décrits **une seule fois** dans
`univers.json`, puis cités par les chapitres où ils apparaissent. Un même
personnage peut apparaître dans plusieurs histoires, de genres différents.

- Un **personnage** : `id`, `name`, `role` (« L'éclaireuse »),
  `description`, `portrait` (image en noir et blanc, carrée, rangée dans
  `images/personnages/<id>.jpg`), `portraitFocus` (facultatif : où est le
  visage, de 0 à 1, pour le recadrage des petits médaillons, par exemple
  `{"x": 0.55, "y": 0.25, "size": 0.6}`) et `secret`
  (facultatif) : `title`, `text` (paragraphes) et `stepsRequired`, le nombre
  de pas à faire **après la rencontre** pour le lire (20 000 par défaut,
  entre 5 000 et 100 000).
- Un **lieu** : `id`, `name`, `region` (écrite sur le timbre),
  `description`, `icon` (dessin du timbre, liste « lieux » dans
  `outils/icones.json`) et `stamp` (image, facultatif, plus tard).
- Dans un chapitre : `"characters": ["elise-marrec"]` et
  `"places": ["port-aven"]`. Le personnage rejoint le Panthéon de
  l'utilisateur, et le lieu son album de timbres, quand il lit ce chapitre.

Les images (`illustration` d'un chapitre, `portrait`, `stamp`) pourront
être des adresses internet (`https://…`) une fois les visuels prêts.

Pour vérifier sur un ordinateur : `python3 outils/verifier.py`.

## Ce qui est publié

`outils/construire_site.py` prépare `v1/catalogue.json` (liste des
histoires et leur « révision »), `v1/histoires/<id>.json` et
`v1/univers.json`. Les fichiers
sont publics : n'y mets rien de personnel.
