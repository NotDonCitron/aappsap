from flask import current_app, render_template_string
from flask_mail import Message
import threading
from app import mail

class EmailService:
    """Async email service for order notifications."""
    
    ORDER_CONFIRMATION_TEMPLATE = """
    <h2>Order Confirmation</h2>
    <p>Thank you for your order, {{ user_name }}!</p>
    <p><strong>Order #:</strong> {{ order_number }}</p>
    <p><strong>Total:</strong> ${{ total }}</p>
    <p>We'll notify you when your order ships.</p>
    """
    
    ORDER_SHIPPED_TEMPLATE = """
    <h2>Your Order Has Shipped!</h2>
    <p>Order #{{ order_number }} is on its way.</p>
    <p><strong>Tracking:</strong> {{ tracking_number }}</p>
    """
    
    LOW_STOCK_TEMPLATE = """
    <h2>Low Stock Alert</h2>
    <p>The following product is running low:</p>
    <p><strong>SKU:</strong> {{ sku }}</p>
    <p><strong>Name:</strong> {{ name }}</p>
    <p><strong>Current Stock:</strong> {{ stock }}</p>
    """
    
    def __init__(self):
        self._enabled = True
    
    def _send_async(self, msg):
        """Send email in background thread."""
        with current_app.app_context():
            mail.send(msg)
    
    def send_email(self, to, subject, body, html=None):
        """Send email asynchronously."""
        if not self._enabled or not current_app.config.get('MAIL_SERVER'):
            current_app.logger.info(f"[EMAIL] To: {to}, Subject: {subject}")
            return
        
        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            body=body,
            html=html
        )
        
        thread = threading.Thread(target=self._send_async, args=[msg])
        thread.start()
    
    def send_order_confirmation(self, order):
        """Send order confirmation email."""
        html = render_template_string(
            self.ORDER_CONFIRMATION_TEMPLATE,
            user_name=order.user.first_name or order.user.email,
            order_number=order.order_number,
            total=order.total_amount
        )
        
        self.send_email(
            to=order.user.email,
            subject=f'Order Confirmation - {order.order_number}',
            body=f'Your order {order.order_number} has been received.',
            html=html
        )
    
    def send_order_shipped(self, order, tracking_number=None):
        """Send shipping notification."""
        html = render_template_string(
            self.ORDER_SHIPPED_TEMPLATE,
            order_number=order.order_number,
            tracking_number=tracking_number or 'N/A'
        )
        
        self.send_email(
            to=order.user.email,
            subject=f'Your Order Has Shipped - {order.order_number}',
            body=f'Order {order.order_number} has shipped.',
            html=html
        )
    
    def send_low_stock_alert(self, product, admin_emails):
        """Send low stock alert to admins."""
        html = render_template_string(
            self.LOW_STOCK_TEMPLATE,
            sku=product.sku,
            name=product.name,
            stock=product.stock
        )
        
        self.send_email(
            to=admin_emails,
            subject=f'Low Stock Alert: {product.sku}',
            body=f'Product {product.name} is low on stock ({product.stock} remaining).',
            html=html
        )

# Global instance
email_service = EmailService()
