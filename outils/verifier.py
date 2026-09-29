#!/usr/bin/env python3
"""Vérifie les fichiers d'histoires avant leur mise en ligne.

Les règles sont celles du cahier des charges de l'app (CLAUDE.md,
sections 4 et 5). Si une erreur est trouvée, le script l'explique en
français et s'arrête : rien n'est publié, l'app continue d'utiliser la
version précédente.

Utilisation : python3 outils/verifier.py
"""

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "histoires"
GENRES = {"adventure", "fantasy", "crime", "romance", "horror", "scienceFiction"}
ICONES = set(json.loads((RACINE / "outils" / "icones.json").read_text("utf-8"))["icones"])
ID_VALIDE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
COULEUR = re.compile(r"^#[0-9A-Fa-f]{6}$")

erreurs = []


def erreur(ou, message):
    erreurs.append(f"- {ou} : {message}")


def texte(obj, champ, ou, facultatif=False):
    valeur = obj.get(champ)
    if valeur is None and facultatif:
        return None
    if not isinstance(valeur, str) or not valeur.strip():
        erreur(ou, f"le champ « {champ} » doit être un texte non vide")
        return None
    return valeur


def nombre_entier(obj, champ, ou):
    valeur = obj.get(champ)
    if not isinstance(valeur, int) or isinstance(valeur, bool):
        erreur(ou, f"le champ « {champ} » doit être un nombre entier")
        return None
    return valeur


def verifier_histoire(id_attendu, souvenirs_vus):
    fichier = DOSSIER / f"{id_attendu}.json"
    ou = fichier.name
    if not fichier.exists():
        erreur("index.json", f"l'histoire « {id_attendu} » est listée mais {ou} n'existe pas")
        return
    try:
        h = json.loads(fichier.read_text("utf-8"))
    except json.JSONDecodeError as e:
        erreur(ou, f"JSON invalide (ligne {e.lineno}, colonne {e.colno}) : {e.msg}")
        return

    if h.get("id") != id_attendu:
        erreur(ou, f"le champ « id » vaut « {h.get('id')} » au lieu de « {id_attendu} »")
    for champ in ("title", "hook", "summary", "themeId"):
        texte(h, champ, ou)
    if h.get("genre") not in GENRES:
        erreur(ou, f"genre « {h.get('genre')} » inconnu (possibles : {', '.join(sorted(GENRES))})")
    if not isinstance(h.get("isFree"), bool):
        erreur(ou, "le champ « isFree » doit valoir true ou false")
    if "isNew" in h and h["isNew"] is not None and not isinstance(h["isNew"], bool):
        erreur(ou, "le champ « isNew » doit valoir true ou false")

    dos = h.get("spine")
    if not isinstance(dos, dict):
        erreur(ou, "le champ « spine » (dos du livre) est manquant")
    else:
        if not isinstance(dos.get("color"), str) or not COULEUR.match(dos["color"]):
            erreur(ou, "spine.color doit être une couleur comme « #7A2E1C »")
        for champ, mini, maxi in (("width", 28, 60), ("height", 70, 110)):
            v = dos.get(champ)
            if not isinstance(v, (int, float)) or not mini <= v <= maxi:
                erreur(ou, f"spine.{champ} doit être un nombre entre {mini} et {maxi}")

    chapitres = h.get("chapters")
    if not isinstance(chapitres, list):
        erreur(ou, "le champ « chapters » doit être une liste de chapitres")
        return
    if not 5 <= len(chapitres) <= 10:
        erreur(ou, f"{len(chapitres)} chapitres : il en faut entre 5 et 10")

    souvenirs = []
    for position, c in enumerate(chapitres, start=1):
        ouc = f"{ou}, chapitre {position}"
        if not isinstance(c, dict):
            erreur(ouc, "chapitre illisible")
            continue
        if c.get("number") != position:
            erreur(ouc, f"le numéro vaut {c.get('number')} au lieu de {position}")
        for champ in ("title", "teaser"):
            texte(c, champ, ouc)
        paragraphes = c.get("text")
        if (
            not isinstance(paragraphes, list)
            or not paragraphes
            or not all(isinstance(p, str) and p.strip() for p in paragraphes)
        ):
            erreur(ouc, "« text » doit être une liste de paragraphes non vides")
        pas = nombre_entier(c, "stepsRequired", ouc)
        if pas is not None:
            if position == 1 and pas != 0:
                erreur(ouc, "le chapitre 1 est offert : « stepsRequired » doit valoir 0")
            if position > 1 and not 3000 <= pas <= 5000:
                erreur(ouc, f"{pas} pas : il faut entre 3000 et 5000")
        souvenirs.append((ouc, c.get("souvenir")))
    souvenirs.append((f"{ou}, souvenir final", h.get("finalSouvenir")))

    for ous, s in souvenirs:
        if not isinstance(s, dict):
            erreur(ous, "le souvenir est manquant")
            continue
        sid = texte(s, "id", ous)
        texte(s, "name", ous)
        if s.get("icon") not in ICONES:
            erreur(ous, f"icône « {s.get('icon')} » inconnue de l'app (voir outils/icones.json)")
        if sid:
            if not sid.startswith(f"{id_attendu}."):
                erreur(ous, f"l'id du souvenir doit commencer par « {id_attendu}. »")
            if sid in souvenirs_vus:
                erreur(ous, f"l'id de souvenir « {sid} » est déjà utilisé")
            souvenirs_vus.add(sid)


def main():
    try:
        index = json.loads((DOSSIER / "index.json").read_text("utf-8"))
        ids = index["stories"]
        assert isinstance(ids, list) and all(isinstance(i, str) for i in ids)
    except Exception:
        print("Erreur : histoires/index.json doit contenir {\"stories\": [\"id-1\", \"id-2\", …]}")
        return 1

    if len(set(ids)) != len(ids):
        erreur("index.json", "une histoire est listée deux fois")
    for i in ids:
        if not ID_VALIDE.match(i):
            erreur("index.json", f"« {i} » : l'identifiant doit être en minuscules, avec des tirets")

    souvenirs_vus = set()
    for i in ids:
        verifier_histoire(i, souvenirs_vus)

    oubliees = sorted(
        p.stem for p in DOSSIER.glob("*.json") if p.name != "index.json" and p.stem not in ids
    )
    for o in oubliees:
        print(f"Attention : {o}.json n'est pas listée dans index.json (elle ne sera pas publiée).")

    if erreurs:
        print(f"{len(erreurs)} erreur(s) à corriger :")
        print("\n".join(erreurs))
        return 1
    print(f"Tout est bon : {len(ids)} histoires vérifiées.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
