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
_ICONES = json.loads((RACINE / "outils" / "icones.json").read_text("utf-8"))
ICONES = set(_ICONES["icones"])
ICONES_LIEUX = set(_ICONES["lieux"])
UNIVERS = DOSSIER / "univers.json"
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


def verifier_univers():
    """Vérifie univers.json (personnages et lieux partagés entre les
    histoires) et renvoie les identifiants connus."""
    ou = UNIVERS.name
    if not UNIVERS.exists():
        return set(), set()
    try:
        u = json.loads(UNIVERS.read_text("utf-8"))
    except json.JSONDecodeError as e:
        erreur(ou, f"JSON invalide (ligne {e.lineno}, colonne {e.colno}) : {e.msg}")
        return set(), set()

    personnages, lieux = set(), set()
    for liste, cle in ((u.get("characters"), "characters"), (u.get("places"), "places")):
        if not isinstance(liste, list):
            erreur(ou, f"le champ « {cle} » doit être une liste")
    for p in u.get("characters") or []:
        pid = p.get("id") if isinstance(p, dict) else None
        oup = f"{ou}, personnage « {pid} »"
        if not isinstance(p, dict) or not isinstance(pid, str) or not ID_VALIDE.match(pid):
            erreur(ou, f"personnage à l'identifiant invalide : {pid!r}")
            continue
        if pid in personnages:
            erreur(oup, "identifiant déjà utilisé")
        personnages.add(pid)
        for champ in ("name", "role", "description"):
            texte(p, champ, oup)
        texte(p, "portrait", oup, facultatif=True)
        secret = p.get("secret")
        if secret is not None:
            ous = f"{oup}, secret"
            if not isinstance(secret, dict):
                erreur(ous, "le secret doit être un objet")
                continue
            texte(secret, "title", ous)
            paragraphes = secret.get("text")
            if (
                not isinstance(paragraphes, list)
                or not paragraphes
                or not all(isinstance(t, str) and t.strip() for t in paragraphes)
            ):
                erreur(ous, "« text » doit être une liste de paragraphes non vides")
            pas = secret.get("stepsRequired", 20000)
            if not isinstance(pas, int) or isinstance(pas, bool) or not 5000 <= pas <= 100000:
                erreur(ous, "« stepsRequired » doit être un nombre entre 5000 et 100000")
    for l in u.get("places") or []:
        lid = l.get("id") if isinstance(l, dict) else None
        oul = f"{ou}, lieu « {lid} »"
        if not isinstance(l, dict) or not isinstance(lid, str) or not ID_VALIDE.match(lid):
            erreur(ou, f"lieu à l'identifiant invalide : {lid!r}")
            continue
        if lid in lieux:
            erreur(oul, "identifiant déjà utilisé")
        lieux.add(lid)
        for champ in ("name", "region", "description"):
            texte(l, champ, oul)
        texte(l, "stamp", oul, facultatif=True)
        if l.get("icon") not in ICONES_LIEUX:
            erreur(oul, f"dessin « {l.get('icon')} » inconnu (possibles : {', '.join(sorted(ICONES_LIEUX))})")
    return personnages, lieux


def verifier_histoire(id_attendu, souvenirs_vus, personnages=frozenset(), lieux=frozenset()):
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
        texte(c, "illustration", ouc, facultatif=True)
        for cle, connus, nom in (("characters", personnages, "personnage"), ("places", lieux, "lieu")):
            ids = c.get(cle)
            if ids is None:
                continue
            if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
                erreur(ouc, f"« {cle} » doit être une liste d'identifiants")
                continue
            for i in ids:
                if i not in connus:
                    erreur(ouc, f"{nom} « {i} » absent de univers.json")
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

    personnages, lieux = verifier_univers()
    souvenirs_vus = set()
    for i in ids:
        verifier_histoire(i, souvenirs_vus, personnages, lieux)

    oubliees = sorted(
        p.stem
        for p in DOSSIER.glob("*.json")
        if p.name not in ("index.json", UNIVERS.name) and p.stem not in ids
    )
    for o in oubliees:
        print(f"Attention : {o}.json n'est pas listée dans index.json (elle ne sera pas publiée).")

    if erreurs:
        print(f"{len(erreurs)} erreur(s) à corriger :")
        print("\n".join(erreurs))
        return 1
    print(
        f"Tout est bon : {len(ids)} histoires, {len(personnages)} personnages "
        f"et {len(lieux)} lieux vérifiés."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
