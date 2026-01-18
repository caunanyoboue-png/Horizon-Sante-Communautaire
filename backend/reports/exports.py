from __future__ import annotations

from io import BytesIO

from patients.models import Consultation, Patient


def export_patients_xlsx() -> bytes:
    try:
        from openpyxl import Workbook
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Dépendance manquante: openpyxl. Installe-la avec: pip install -r requirements.txt"
        ) from exc

    wb = Workbook()
    ws = wb.active
    ws.title = "Patients"

    ws.append(["Code", "Nom", "Prénoms", "Sexe", "Date naissance", "Téléphone", "Zone", "Adresse"])

    for p in Patient.objects.all().order_by("nom", "prenoms"):
        ws.append(
            [
                p.code_patient,
                p.nom,
                p.prenoms,
                p.sexe,
                str(p.date_naissance or ""),
                p.telephone,
                p.get_zone_display(),
                p.adresse,
            ]
        )

    out = BytesIO()
    wb.save(out)
    return out.getvalue()


def export_consultations_xlsx() -> bytes:
    try:
        from openpyxl import Workbook
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Dépendance manquante: openpyxl. Installe-la avec: pip install -r requirements.txt"
        ) from exc

    wb = Workbook()
    ws = wb.active
    ws.title = "Consultations"

    ws.append(["Patient", "Date", "Motif", "Observation"])

    for c in Consultation.objects.select_related("patient").all().order_by("-date_consultation"):
        ws.append(
            [
                f"{c.patient.code_patient} - {c.patient.nom} {c.patient.prenoms}",
                c.date_consultation.strftime("%Y-%m-%d %H:%M"),
                c.motif,
                c.observation,
            ]
        )

    out = BytesIO()
    wb.save(out)
    return out.getvalue()
