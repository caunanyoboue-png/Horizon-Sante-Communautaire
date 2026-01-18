from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SmsSendResult:
    success: bool
    provider: str = "stub"
    message_id: str = ""
    error: str = ""


class SmsProvider:
    """Provider SMS (stub).

    Remplace cette classe par l'intégration d'un fournisseur (Twilio, Orange, MTN, etc.).
    """

    def send_sms(self, phone: str, message: str) -> SmsSendResult:
        # Ici: stub => on considère l'envoi comme réussi.
        # Pour un vrai provider: implémenter l'appel API + gestion erreurs.
        if not phone:
            return SmsSendResult(success=False, error="Téléphone manquant")
        return SmsSendResult(success=True, provider="stub", message_id="stub-message-id")
