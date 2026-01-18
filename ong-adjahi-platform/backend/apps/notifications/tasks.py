"""
Celery tasks for Notifications
"""

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import Notification, SMSLog, EmailLog


@shared_task
def send_sms(phone_number, message, reference_type='', reference_id=''):
    """
    Send SMS using Twilio or AfricasTalking
    """
    try:
        # Using Twilio
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            from twilio.rest import Client
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            twilio_message = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            # Log SMS
            SMSLog.objects.create(
                phone_number=phone_number,
                message=message,
                status='SENT',
                provider_response=twilio_message.sid
            )
            
            return {
                'success': True,
                'provider': 'twilio',
                'sid': twilio_message.sid
            }
        
        # Alternative: AfricasTalking (uncomment if using)
        # elif hasattr(settings, 'AFRICASTALKING_USERNAME'):
        #     import africastalking
        #     africastalking.initialize(
        #         settings.AFRICASTALKING_USERNAME,
        #         settings.AFRICASTALKING_API_KEY
        #     )
        #     sms = africastalking.SMS
        #     response = sms.send(message, [phone_number])
        #     
        #     SMSLog.objects.create(
        #         phone_number=phone_number,
        #         message=message,
        #         status='SENT',
        #         provider_response=str(response)
        #     )
        #     
        #     return {'success': True, 'provider': 'africastalking'}
        
        else:
            # No SMS provider configured - log only
            SMSLog.objects.create(
                phone_number=phone_number,
                message=message,
                status='SKIPPED',
                provider_response='No SMS provider configured'
            )
            
            return {
                'success': False,
                'error': 'No SMS provider configured'
            }
    
    except Exception as e:
        # Log failed SMS
        SMSLog.objects.create(
            phone_number=phone_number,
            message=message,
            status='FAILED',
            provider_response=str(e)
        )
        
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def send_email(to_email, subject, message, html_message=None):
    """
    Send email using Django email backend
    """
    try:
        from django.core.mail import send_mail
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Log email
        EmailLog.objects.create(
            to_email=to_email,
            subject=subject,
            message=message,
            status='SENT'
        )
        
        return {
            'success': True,
            'to': to_email
        }
    
    except Exception as e:
        # Log failed email
        EmailLog.objects.create(
            to_email=to_email,
            subject=subject,
            message=message,
            status='FAILED',
            error_message=str(e)
        )
        
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def send_cpn_reminder_sms(reminder_id):
    """
    Send CPN reminder SMS
    """
    from apps.cpn.models import CPNReminder
    
    try:
        reminder = CPNReminder.objects.get(id=reminder_id)
        
        result = send_sms.delay(
            phone_number=reminder.pregnancy.patient.phone,
            message=reminder.message,
            reference_type='cpn_reminder',
            reference_id=str(reminder_id)
        )
        
        # Update reminder status
        reminder.status = 'SENT'
        reminder.sent_at = timezone.now()
        reminder.save()
        
        return result
    
    except CPNReminder.DoesNotExist:
        return {'success': False, 'error': 'Reminder not found'}
    except Exception as e:
        reminder.status = 'FAILED'
        reminder.error_message = str(e)
        reminder.save()
        
        return {'success': False, 'error': str(e)}


@shared_task
def send_bulk_sms(phone_numbers, message):
    """
    Send SMS to multiple recipients
    """
    results = []
    
    for phone in phone_numbers:
        result = send_sms.delay(phone, message)
        results.append({
            'phone': phone,
            'result': result
        })
    
    return {
        'total': len(phone_numbers),
        'results': results
    }


@shared_task
def send_notification(user_id, notification_type, subject, message):
    """
    Create and send a notification
    """
    from apps.authentication.models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        # Create notification record
        notification = Notification.objects.create(
            recipient=user,
            recipient_email=user.email,
            recipient_phone=user.phone,
            notification_type=notification_type,
            subject=subject,
            message=message
        )
        
        # Send based on type
        if notification_type == 'SMS':
            result = send_sms.delay(user.phone, message)
        elif notification_type == 'EMAIL':
            result = send_email.delay(user.email, subject, message)
        else:
            result = {'success': True, 'type': 'in_app_only'}
        
        # Update notification status
        if result.get('success'):
            notification.status = 'SENT'
            notification.sent_at = timezone.now()
        else:
            notification.status = 'FAILED'
            notification.error_message = result.get('error', '')
        
        notification.save()
        
        return {
            'success': True,
            'notification_id': notification.id
        }
    
    except User.DoesNotExist:
        return {'success': False, 'error': 'User not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
