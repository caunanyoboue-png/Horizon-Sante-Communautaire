from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SmsSendResult:
    success: bool
    provider: str = "stub"
    message_id: str = ""
    error: str = ""


class SmsProvider:
    """Provider SMS (simulation locale).

    En dev, écrit les SMS dans un fichier local pour vérification.
    En prod, remplacer par l'intégration d'un fournisseur (Twilio, Orange, MTN, etc.).
    """

    def send_sms(self, phone: str, message: str) -> SmsSendResult:
        if not phone:
            return SmsSendResult(success=False, error="Téléphone manquant")
        
        # Simulation d'envoi en écrivant dans un fichier log
        try:
            import os
            from django.utils import timezone
            
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(os.path.join(log_dir, "sms_outbox.log"), "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] TO: {phone} | MSG: {message}\n")
                
            return SmsSendResult(success=True, provider="local_file", message_id=f"local-{timezone.now().timestamp()}")
        except Exception as e:
            return SmsSendResult(success=False, error=str(e))
