from __future__ import annotations

import os
import re
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from achievements.models import Achievement, AchievementImage, AREAS


class Command(BaseCommand):
    help = (
        "Import achievements and images from default 'engazat.txt' + 'ENGAZAT'"
        " and also supports the alternative Arabic folder 'باقي الانجازات' with"
        " 'باقى الانجازات.txt' + 'الصور الخاصة بالانجازات' if present."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--base",
            type=str,
            default=str(Path.cwd()),
            help="Base directory that contains 'achevments file' folder",
        )

    def handle(self, *args, **options):
        # Build a list of (text_file, images_dir) sources to import
        sources: list[tuple[Path, Path]] = []

        base_dir_default = Path(options["base"]) / "achevments file"
        txt_default = base_dir_default / "engazat.txt"
        imgs_default = base_dir_default / "ENGAZAT"
        if txt_default.exists() and imgs_default.exists():
            sources.append((txt_default, imgs_default))

        base_dir_ar = Path(options["base"]) / "باقي الانجازات"
        txt_ar = base_dir_ar / "باقى الانجازات.txt"
        imgs_ar = base_dir_ar / "الصور الخاصة بالانجازات"
        if txt_ar.exists() and imgs_ar.exists():
            sources.append((txt_ar, imgs_ar))

        if not sources:
            raise CommandError(
                "No sources found. Expected either 'achevments file/engazat.txt' + 'ENGAZAT'"
                " or 'باقي الانجازات/باقى الانجازات.txt' + 'الصور الخاصة بالانجازات'."
            )

        area_values = {a for a, _ in AREAS}

        created_without_image = 0
        created_total = 0

        for txt_path, images_dir in sources:
            self.stdout.write(self.style.NOTICE(f"Reading: {txt_path}"))
            raw = txt_path.read_text(encoding="utf-8", errors="ignore")

            # Split blocks by delimiter lines
            blocks = [b.strip() for b in re.split(r"-+\s*\n", raw) if b.strip()]
            self.stdout.write(self.style.NOTICE(f"Found {len(blocks)} blocks in {txt_path.name}"))
            for block in blocks:
                # Extract fields
                image_lines = re.findall(r"^اسم الصورة\s*:\s*(.+)$", block, re.MULTILINE)
                area_match = re.search(r"^اسم الدائرة\s*:\s*(.+)$", block, re.MULTILINE)
                village_match = re.search(r"^اسم القريه\s*:\s*(.+)$", block, re.MULTILINE)
                desc_match = re.search(r"^الوصف الخاص بالصورة\s*:\s*(.+)$", block, re.MULTILINE)

                if not (area_match and village_match and desc_match):
                    continue

                area_text = area_match.group(1).strip()
                area = area_text if area_text in area_values else next(iter(area_values))

                village = village_match.group(1).strip()
                description = desc_match.group(1).strip()

            # Creative title from village and a concise hint from description
                hint = description.split(" ")[:6]
                title = f"{village} – {' '.join(hint)}".strip()

                with transaction.atomic():
                    achievement = Achievement.objects.create(
                        title=title,
                        description=description,
                        area=area,
                    )
                    created_total += 1

                # Parse possibly multiple image names across one or more lines
                    image_names: list[str] = []
                    for line in image_lines:
                    # Split by whitespace and parentheses commas
                        parts = re.split(r"\s+", line.strip())
                        for p in parts:
                            p = p.strip().strip(",")
                            if p:
                                image_names.append(p)

                # Normalize to possible files with common extensions
                    exts = [".jpg", ".jpeg", ".png", ".jfif", ".JPG", ".JPEG", ".PNG", ".JFIF"]

                    found_any = False
                    for base in image_names:
                    # Some names come without extension or with (1)
                        base_clean = base
                    # keep provided extension if any
                        cand_paths: list[Path] = []
                        bpath = images_dir / base_clean
                        cand_paths.append(bpath)
                        if bpath.suffix == "":
                            for ext in exts:
                                cand_paths.append(images_dir / f"{base_clean}{ext}")

                    # also try removing spaces like " (1)"
                        if " (" in base_clean:
                            base_alt = re.sub(r"\s*\(\d+\)$", "", base_clean)
                            cand_paths.append(images_dir / base_alt)
                            if Path(base_alt).suffix == "":
                                for ext in exts:
                                    cand_paths.append(images_dir / f"{base_alt}{ext}")

                        for cand in cand_paths:
                            if cand.exists() and cand.is_file():
                                with cand.open("rb") as f:
                                    AchievementImage.objects.create(
                                        achievement=achievement,
                                        image=File(f, name=cand.name),
                                    )
                                found_any = True
                                break

                    if not found_any:
                        created_without_image += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_total} achievements"))
        if created_without_image:
            self.stdout.write(self.style.WARNING(f"{created_without_image} achievements created without images"))


