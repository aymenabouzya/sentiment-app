"""Vérifie le contenu et l'installation isolée du livrable TP4."""

import os
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
DIST = RACINE / "dist"
WHEEL = DIST / "sentiment_app-1.0.0-py3-none-any.whl"
SDIST = DIST / "sentiment_app-1.0.0.tar.gz"
MODELE = "sentiment_app/modele/sentiment.joblib"
RAPPORT = RACINE / "docs" / "livrable-tp4.txt"


class Verification:
    def __init__(self) -> None:
        self.lignes: list[str] = []
        self.conforme = True

    def noter(self, ok: bool, message: str, detail: str = "") -> bool:
        statut = "OK" if ok else "ÉCHEC"
        ligne = f"[{statut}] {message}"
        if detail:
            ligne += f" : {detail}"
        self.lignes.append(ligne)
        self.conforme = self.conforme and ok
        print(ligne)
        return ok

    def terminer(self) -> int:
        bilan = "CONFORME" if self.conforme else "NON CONFORME"
        self.lignes.append(f"Bilan : {bilan}")
        print(f"Bilan : {bilan}")
        RAPPORT.parent.mkdir(parents=True, exist_ok=True)
        RAPPORT.write_text("\n".join(self.lignes) + "\n", encoding="utf-8")
        print(f"Rapport : {RAPPORT.relative_to(RACINE)}")
        return 0 if self.conforme else 1


def lancer(
    commande: list[str], cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    environnement = {**os.environ, **(env or {})}
    try:
        return subprocess.run(
            commande,
            cwd=cwd,
            env=environnement,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=300,
        )
    except (OSError, subprocess.TimeoutExpired) as erreur:
        return subprocess.CompletedProcess(commande, 1, "", str(erreur))


def derniere_ligne(sortie: str) -> str:
    lignes = sortie.strip().splitlines()
    return lignes[-1] if lignes else ""


def main() -> int:
    verification = Verification()
    fichiers = sorted(path.name for path in DIST.iterdir()) if DIST.exists() else []
    verification.noter(WHEEL.is_file(), "roue présente", WHEEL.name if WHEEL.exists() else "")
    verification.noter(SDIST.is_file(), "distribution source présente", SDIST.name if SDIST.exists() else "")
    verification.noter(
        fichiers == [WHEEL.name, SDIST.name],
        "aucun autre fichier dans dist/",
        ", ".join(fichiers) or "(dossier absent)",
    )

    noms: set[str] = set()
    if WHEEL.is_file():
        try:
            with zipfile.ZipFile(WHEEL) as archive:
                noms = set(archive.namelist())
                metadonnees = next(
                    (nom for nom in noms if nom.endswith(".dist-info/METADATA")), ""
                )
                entree = next(
                    (nom for nom in noms if nom.endswith(".dist-info/entry_points.txt")), ""
                )
                contenu = archive.read(metadonnees).decode("utf-8") if metadonnees else ""
                entree_contenu = archive.read(entree).decode("utf-8") if entree else ""
                verification.noter(MODELE in noms, "modèle embarqué dans la roue")
                verification.noter(
                    "Name: sentiment-app" in contenu and "Version: 1.0.0" in contenu,
                    "métadonnées de la roue conformes",
                )
                verification.noter(
                    "sentiment = sentiment_app.cli:main" in entree_contenu,
                    "commande « sentiment » déclarée",
                )
                verification.noter(
                    not any("/tests/" in nom or nom.startswith("tests/") for nom in noms),
                    "pas de tests dans la roue",
                )
        except (OSError, zipfile.BadZipFile, UnicodeDecodeError) as erreur:
            verification.noter(False, "inspection de la roue", str(erreur))
    else:
        verification.noter(False, "modèle embarqué dans la roue", "roue absente")
        verification.noter(False, "métadonnées de la roue conformes", "roue absente")
        verification.noter(False, "commande « sentiment » déclarée", "roue absente")
        verification.noter(False, "pas de tests dans la roue", "roue absente")

    changelog = RACINE / "CHANGELOG.md"
    version_documentee = changelog.is_file() and "## [1.0.0] - " in changelog.read_text(
        encoding="utf-8"
    )
    verification.noter(version_documentee, "CHANGELOG.md décrit cette version : [1.0.0]")

    tag = lancer(
        ["git", "describe", "--tags", "--exact-match", "HEAD"],
        RACINE,
    )
    verification.noter(tag.returncode == 0 and tag.stdout.strip() == "v1.0.0",
                       "étiquette Git sur le dernier commit : v1.0.0")

    if not (WHEEL.is_file() and MODELE in noms):
        return verification.terminer()

    with tempfile.TemporaryDirectory(prefix="verification-livrable-") as temporaire:
        dossier = Path(temporaire)
        environnement = dossier / "env"
        venv.create(environnement, with_pip=True)
        binaires = environnement / ("Scripts" if sys.platform == "win32" else "bin")
        python = binaires / ("python.exe" if sys.platform == "win32" else "python")
        installation = lancer(
            [str(python), "-m", "pip", "install", "-q", str(WHEEL), "pytest"],
            dossier,
        )
        if not verification.noter(
            installation.returncode == 0,
            "installation de la roue dans un environnement neuf",
            derniere_ligne(installation.stderr),
        ):
            return verification.terminer()

        tests = lancer(
            [
                str(python),
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                str(RACINE / "tests" / "test_paquet.py"),
            ],
            dossier,
            {"VERIFICATION_LIVRABLE": "1"},
        )
        bilan = derniere_ligne(tests.stdout)
        verification.noter(
            tests.returncode == 0 and "skipped" not in bilan,
            "tests lancés sur le paquet installé",
            bilan or derniere_ligne(tests.stderr),
        )

        commande = binaires / ("sentiment.exe" if sys.platform == "win32" else "sentiment")
        resultat = lancer(
            [str(commande), "--json", "Livraison rapide, très satisfait"],
            dossier,
        )
        verification.noter(
            resultat.returncode == 0 and '"label"' in resultat.stdout,
            "commande installée",
            resultat.stdout.strip() or derniere_ligne(resultat.stderr),
        )

    return verification.terminer()


if __name__ == "__main__":
    raise SystemExit(main())
