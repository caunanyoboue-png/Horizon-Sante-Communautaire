"""
Celery Configuration for ONG ADJAHI Platform
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('adjahi_platform')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from installed apps
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    # Envoyer rappels CPN quotidiennement à 9h
    'send-cpn-reminders-daily': {
        'task': 'apps.cpn.tasks.send_cpn_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
    # Vérifier consultations manquées chaque jour à 8h
    'check-missed-appointments': {
        'task': 'apps.consultations.tasks.check_missed_appointments',
        'schedule': crontab(hour=8, minute=0),
    },
    # Générer rapport mensuel le 1er de chaque mois à 7h
    'generate-monthly-reports': {
        'task': 'apps.reports.tasks.generate_monthly_reports',
        'schedule': crontab(hour=7, minute=0, day_of_month=1),
    },
    # Sauvegarder la base de données chaque jour à 2h du matin
    'backup-database-daily': {
        'task': 'apps.common.tasks.backup_database',
        'schedule': crontab(hour=2, minute=0),
    },
    # Nettoyer logs anciens chaque dimanche à 3h
    'cleanup-old-logs': {
        'task': 'apps.common.tasks.cleanup_old_logs',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
