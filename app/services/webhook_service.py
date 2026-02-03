import hmac
import hashlib
import json
import threading
import requests
from flask import current_app
from datetime import datetime

class WebhookService:
    """HMAC-signed webhook delivery service."""
    
    def __init__(self):
        self._secret = None
        self._url = None
    
    def _get_secret(self):
        if self._secret is None:
            self._secret = current_app.config.get('WEBHOOK_SECRET', '')
        return self._secret
    
    def _get_url(self):
        if self._url is None:
            self._url = current_app.config.get('WEBHOOK_URL')
        return self._url
    
    def _generate_signature(self, payload):
        """Generate HMAC-SHA256 signature."""
        secret = self._get_secret()
        return hmac.new(
            secret.encode('utf-8'),
            json.dumps(payload, sort_keys=True).encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _send_webhook(self, event, payload):
        """Send webhook request."""
        url = self._get_url()
        if not url:
            current_app.logger.info(f"[WEBHOOK] {event}: {payload}")
            return
        
        webhook_payload = {
            'event': event,
            'timestamp': datetime.utcnow().isoformat(),
            'data': payload
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': self._generate_signature(webhook_payload),
            'X-Webhook-Event': event
        }
        
        try:
            response = requests.post(
                url,
                json=webhook_payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            current_app.logger.info(f"Webhook delivered: {event}")
        except Exception as e:
            current_app.logger.error(f"Webhook failed: {event} - {e}")
    
    def trigger(self, event, data):
        """Trigger webhook asynchronously."""
        thread = threading.Thread(
            target=self._send_webhook,
            args=(event, data)
        )
        thread.start()
    
    def verify_signature(self, payload, signature):
        """Verify incoming webhook signature."""
        expected = self._generate_signature(payload)
        return hmac.compare_digest(expected, signature)

# Global instance
webhook_service = WebhookService()
