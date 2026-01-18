from __future__ import annotations

import gzip
import os
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Sauvegarde la base MySQL via mysqldump dans le dossier backups/."

    def add_arguments(self, parser):
        parser.add_argument("--keep", type=int, default=30, help="Nombre de sauvegardes à conserver")
        parser.add_argument("--gzip", action="store_true", help="Compresser la sauvegarde en .gz")
        parser.add_argument(
            "--mysqldump",
            default=os.getenv("MYSQLDUMP_PATH", "mysqldump"),
            help="Chemin vers mysqldump (ex: C:/.../mysqldump.exe)",
        )

    def handle(self, *args, **options):
        db = settings.DATABASES.get("default", {})
        if db.get("ENGINE") != "django.db.backends.mysql":
            raise CommandError("backup_db supporte uniquement MySQL (ENGINE=django.db.backends.mysql).")

        name = db.get("NAME")
        user = db.get("USER")
        password = db.get("PASSWORD")
        host = db.get("HOST") or "127.0.0.1"
        port = str(db.get("PORT") or "3306")

        if not name:
            raise CommandError("DB_NAME manquant.")
        if not user:
            raise CommandError("DB_USER manquant.")

        backups_dir = Path(settings.BASE_DIR) / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = ".sql.gz" if options["gzip"] else ".sql"
        out_path = backups_dir / f"{name}_{ts}{ext}"

        mysqldump = options["mysqldump"]
        cmd = [
            mysqldump,
            f"--host={host}",
            f"--port={port}",
            f"--user={user}",
            "--single-transaction",
            "--routines",
            "--events",
            name,
        ]

        env = os.environ.copy()
        if password:
            env["MYSQL_PWD"] = password

        try:
            if options["gzip"]:
                with gzip.open(out_path, "wb") as f:
                    proc = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env, check=False)
            else:
                with open(out_path, "wb") as f:
                    proc = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env, check=False)
        except FileNotFoundError as exc:
            raise CommandError(
                f"mysqldump introuvable: {mysqldump}. "
                "Installe MySQL Client ou définis MYSQLDUMP_PATH dans .env"
            ) from exc

        if proc.returncode != 0:
            stderr = (proc.stderr or b"").decode("utf-8", errors="ignore").strip()
            raise CommandError(f"Échec mysqldump (code {proc.returncode}). {stderr}")

        self.stdout.write(self.style.SUCCESS(f"Backup créé: {out_path}"))

        keep = int(options["keep"] or 0)
        if keep > 0:
            backups = sorted(backups_dir.glob(f"{name}_*.sql*"), key=lambda p: p.stat().st_mtime, reverse=True)
            for old in backups[keep:]:
                try:
                    old.unlink()
                except OSError:
                    pass
