from flask import render_template, current_app
from flask_mail import Message
from . import mail
from .models import PagoBarbero
import logging

logger = logging.getLogger(__name__)


def enviar_recibo_pago(pago_id, email_destino=None):
    """
    Envía el recibo de pago de un barbero por email.

    Args:
        pago_id: ID del PagoBarbero a enviar.
        email_destino: Email destino opcional; si no se provee, usa el del barbero.

    Returns:
        dict con 'success' (bool) y 'error' (str, solo si falla).
    """
    try:
        pago = PagoBarbero.query.get(pago_id)
        if not pago:
            return {'success': False, 'error': 'Pago no encontrado'}

        barbero = pago.barber
        email = email_destino or barbero.email

        if not email:
            return {
                'success': False,
                'error': f'El barbero {barbero.name} no tiene email configurado'
            }

        periodo_inicio = pago.fecha_inicio_periodo.strftime('%d/%m/%Y')
        periodo_fin = pago.fecha_fin_periodo.strftime('%d/%m/%Y')
        subject = f'Recibo de Pago — {barbero.name} ({periodo_inicio} al {periodo_fin})'

        html_body = render_template(
            'emails/recibo_pago.html',
            pago=pago,
            barbero=barbero,
            periodo_inicio=periodo_inicio,
            periodo_fin=periodo_fin,
        )

        msg = Message(
            subject=subject,
            recipients=[email],
            html=html_body,
        )

        mail.send(msg)
        logger.info('Recibo de pago %d enviado a %s', pago_id, email)
        return {'success': True}

    except Exception as e:
        logger.error('Error al enviar recibo de pago %d: %s', pago_id, str(e))
        return {
            'success': False,
            'error': 'No se pudo enviar el email. Verificá la configuración SMTP o intentá más tarde.'
        }
