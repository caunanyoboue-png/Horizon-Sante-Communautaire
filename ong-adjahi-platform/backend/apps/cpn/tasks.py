"""
Celery tasks for CPN module
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Pregnancy, CPNConsultation, CPNReminder


@shared_task
def send_cpn_reminders():
    """
    Send CPN reminders to patients
    Scheduled to run daily at 9:00 AM
    """
    today = timezone.now().date()
    
    # Get all pending reminders for today or overdue
    reminders = CPNReminder.objects.filter(
        status='PENDING',
        reminder_date__lte=today
    )
    
    sent_count = 0
    failed_count = 0
    
    for reminder in reminders:
        try:
            # Import SMS task
            from apps.notifications.tasks import send_sms
            
            # Send SMS
            patient = reminder.pregnancy.patient
            send_sms.delay(
                phone_number=patient.phone,
                message=reminder.message
            )
            
            # Update reminder status
            reminder.status = 'SENT'
            reminder.sent_at = timezone.now()
            reminder.save()
            
            sent_count += 1
            
        except Exception as e:
            reminder.status = 'FAILED'
            reminder.error_message = str(e)
            reminder.save()
            failed_count += 1
    
    return {
        'sent': sent_count,
        'failed': failed_count,
        'total': reminders.count()
    }


@shared_task
def create_cpn_reminders():
    """
    Create automatic CPN reminders for upcoming consultations
    Run daily
    """
    today = timezone.now().date()
    two_weeks = today + timedelta(days=14)
    
    # Get all ongoing pregnancies
    pregnancies = Pregnancy.objects.filter(status='ONGOING')
    
    created_count = 0
    
    for pregnancy in pregnancies:
        # Get last CPN consultation
        last_cpn = pregnancy.cpn_consultations.order_by('-consultation_date').first()
        
        if last_cpn and last_cpn.next_appointment_date:
            # Check if reminder needed (2 weeks before appointment)
            if last_cpn.next_appointment_date <= two_weeks:
                # Check if reminder already exists
                existing = CPNReminder.objects.filter(
                    pregnancy=pregnancy,
                    cpn_consultation=last_cpn,
                    reminder_date=last_cpn.next_appointment_date - timedelta(days=14)
                ).exists()
                
                if not existing:
                    # Create reminder
                    message = (
                        f"Bonjour {pregnancy.patient.first_name}, "
                        f"rappel de votre consultation {last_cpn.next_cpn_type} "
                        f"prévue le {last_cpn.next_appointment_date.strftime('%d/%m/%Y')}. "
                        f"ONG ADJAHI"
                    )
                    
                    CPNReminder.objects.create(
                        pregnancy=pregnancy,
                        cpn_consultation=last_cpn,
                        reminder_date=last_cpn.next_appointment_date - timedelta(days=14),
                        message=message
                    )
                    
                    created_count += 1
    
    return {
        'created': created_count
    }


@shared_task
def update_pregnancy_risk_levels():
    """
    Update pregnancy risk levels based on latest CPN data
    Run daily
    """
    from django.db.models import Q
    
    pregnancies = Pregnancy.objects.filter(status='ONGOING')
    updated_count = 0
    
    for pregnancy in pregnancies:
        # Get latest CPN
        latest_cpn = pregnancy.cpn_consultations.order_by('-consultation_date').first()
        
        if not latest_cpn:
            continue
        
        # Calculate risk level
        risk_factors = 0
        
        # Medical conditions
        if pregnancy.has_diabetes:
            risk_factors += 2
        if pregnancy.has_hypertension:
            risk_factors += 2
        if pregnancy.has_anemia:
            risk_factors += 1
        
        # CPN findings
        if latest_cpn.is_high_blood_pressure:
            risk_factors += 2
        if latest_cpn.is_anemic:
            risk_factors += 1
        if latest_cpn.protein_in_urine:
            risk_factors += 1
        if latest_cpn.hiv_test_result and 'positif' in latest_cpn.hiv_test_result.lower():
            risk_factors += 2
        
        # Age risk
        patient_age = pregnancy.patient.age
        if patient_age < 18 or patient_age > 35:
            risk_factors += 1
        
        # Determine risk level
        old_risk = pregnancy.risk_level
        if risk_factors >= 4:
            pregnancy.risk_level = 'HIGH'
        elif risk_factors >= 2:
            pregnancy.risk_level = 'MEDIUM'
        else:
            pregnancy.risk_level = 'LOW'
        
        if old_risk != pregnancy.risk_level:
            pregnancy.save()
            updated_count += 1
    
    return {
        'updated': updated_count
    }


@shared_task
def check_overdue_pregnancies():
    """
    Check for overdue pregnancies (>42 weeks)
    Send alerts to medical staff
    """
    today = timezone.now().date()
    
    # Get pregnancies past expected delivery date
    overdue = Pregnancy.objects.filter(
        status='ONGOING',
        expected_delivery_date__lt=today - timedelta(weeks=1)
    )
    
    alerts_sent = 0
    
    for pregnancy in overdue:
        weeks_overdue = (today - pregnancy.expected_delivery_date).days // 7
        
        if weeks_overdue >= 2:
            # Send alert to assigned midwife
            from apps.notifications.tasks import send_email
            
            if pregnancy.assigned_midwife and pregnancy.assigned_midwife.email:
                message = (
                    f"ALERTE: La patiente {pregnancy.patient.get_full_name()} "
                    f"(ID: {pregnancy.patient.patient_id}) est en retard de {weeks_overdue} semaines "
                    f"par rapport à la date prévue d'accouchement ({pregnancy.expected_delivery_date}). "
                    f"Veuillez effectuer un suivi urgent."
                )
                
                send_email.delay(
                    to_email=pregnancy.assigned_midwife.email,
                    subject="ALERTE: Grossesse en retard",
                    message=message
                )
                
                alerts_sent += 1
    
    return {
        'overdue_pregnancies': overdue.count(),
        'alerts_sent': alerts_sent
    }
