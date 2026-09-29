#!/usr/bin/env python3
"""Prépare le dossier publié sur GitHub Pages (_site/).

L'app lit :
- v1/catalogue.json : la liste des histoires, avec une « révision » par
  histoire (calculée à partir du contenu du fichier) ; l'app ne
  retélécharge une histoire que si sa révision a changé ;
- v1/histoires/<id>.json : chaque histoire.

Le « v1 » permettra de changer de format plus tard sans casser les
anciennes versions de l'app.
"""

import hashlib
import json
import shutil
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "histoires"
SITE = RACINE / "_site"
SORTIE = SITE / "v1"


def main():
    ids = json.loads((SOURCE / "index.json").read_text("utf-8"))["stories"]
    if SITE.exists():
        shutil.rmtree(SITE)
    (SORTIE / "histoires").mkdir(parents=True)

    catalogue = {"format": 1, "stories": []}
    for i in ids:
        contenu = (SOURCE / f"{i}.json").read_bytes()
        (SORTIE / "histoires" / f"{i}.json").write_bytes(contenu)
        revision = hashlib.sha256(contenu).hexdigest()[:12]
        catalogue["stories"].append({"id": i, "revision": revision})

    (SORTIE / "catalogue.json").write_text(
        json.dumps(catalogue, ensure_ascii=False, indent=2), "utf-8"
    )
    # Pas de traitement Jekyll : les fichiers sont servis tels quels.
    (SITE / ".nojekyll").write_text("")
    (SITE / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Histoires</title>"
        "<p>Contenu de l'app de marche : voir v1/catalogue.json.</p>",
        "utf-8",
    )
    print(f"Site prêt : {len(ids)} histoires.")


if __name__ == "__main__":
    main()
