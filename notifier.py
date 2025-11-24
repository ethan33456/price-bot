"""Notification system for alerting about deals."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from datetime import datetime
import config


class Notifier:
    """Handle notifications for deals found."""
    
    def __init__(self):
        self.email_enabled = config.ENABLE_EMAIL_NOTIFICATIONS
        
    def notify(self, deals: List[Dict]) -> None:
        """
        Send notifications about deals found.
        
        Args:
            deals: List of deal dictionaries to notify about
        """
        if not deals:
            return
        
        # Always print to console
        self._console_notification(deals)
        
        # Send email if enabled
        if self.email_enabled:
            try:
                self._email_notification(deals)
            except Exception as e:
                print(f"Failed to send email notification: {e}")
    
    def _console_notification(self, deals: List[Dict]) -> None:
        """
        Print deals to console.
        
        Args:
            deals: List of deal dictionaries
        """
        print("\n" + "="*80)
        print(f"🚨 ALERT: {len(deals)} DEEP DISCOUNT(S) FOUND!")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        for i, deal in enumerate(deals, 1):
            print(f"Deal #{i}:")
            print(f"  Product: {deal['name']}")
            print(f"  Current Price: ${deal['current_price']:.2f}")
            print(f"  Retail Price: ${deal['retail_price']:.2f}")
            print(f"  Discount: {deal['discount_percent']:.1f}%")
            print(f"  Savings: ${deal['retail_price'] - deal['current_price']:.2f}")
            print(f"  URL: {deal['url']}")
            print()
        
        print("="*80 + "\n")
    
    def _email_notification(self, deals: List[Dict]) -> None:
        """
        Send email notification about deals.
        
        Args:
            deals: List of deal dictionaries
        """
        if not all([config.EMAIL_FROM, config.EMAIL_TO, config.EMAIL_PASSWORD]):
            print("Email credentials not configured. Skipping email notification.")
            return
        
        subject = f"🚨 {len(deals)} Best Buy Deal(s) Found - 65%+ Off!"
        body = self._format_email_body(deals)
        
        msg = MIMEMultipart('alternative')
        msg['From'] = config.EMAIL_FROM
        msg['To'] = config.EMAIL_TO
        msg['Subject'] = subject
        
        # Create both plain text and HTML versions
        text_part = MIMEText(body, 'plain')
        html_part = MIMEText(self._format_email_html(deals), 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        try:
            with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                server.starttls()
                server.login(config.EMAIL_FROM, config.EMAIL_PASSWORD)
                server.send_message(msg)
            
            print(f"✅ Email notification sent to {config.EMAIL_TO}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            raise
    
    def _format_email_body(self, deals: List[Dict]) -> str:
        """
        Format plain text email body.
        
        Args:
            deals: List of deal dictionaries
            
        Returns:
            Formatted email body string
        """
        body = f"Found {len(deals)} deep discount(s) on Best Buy!\n\n"
        body += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        body += "="*60 + "\n\n"
        
        for i, deal in enumerate(deals, 1):
            body += f"Deal #{i}:\n"
            body += f"Product: {deal['name']}\n"
            body += f"Current Price: ${deal['current_price']:.2f}\n"
            body += f"Retail Price: ${deal['retail_price']:.2f}\n"
            body += f"Discount: {deal['discount_percent']:.1f}%\n"
            body += f"You Save: ${deal['retail_price'] - deal['current_price']:.2f}\n"
            body += f"Link: {deal['url']}\n"
            body += "\n" + "-"*60 + "\n\n"
        
        return body
    
    def _format_email_html(self, deals: List[Dict]) -> str:
        """
        Format HTML email body.
        
        Args:
            deals: List of deal dictionaries
            
        Returns:
            Formatted HTML email body string
        """
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #0046be; color: white; padding: 20px; text-align: center; border-radius: 5px; }
                .deal { background-color: #f5f5f5; margin: 20px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #0046be; }
                .deal-title { font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #0046be; }
                .price-info { margin: 10px 0; }
                .current-price { font-size: 24px; font-weight: bold; color: #c5281c; }
                .retail-price { text-decoration: line-through; color: #666; }
                .discount { background-color: #c5281c; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
                .savings { color: #008a00; font-weight: bold; }
                .button { display: inline-block; background-color: #0046be; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; }
                .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Best Buy Deals Alert!</h1>
                    <p>Found """ + str(len(deals)) + """ deep discount(s) - 65%+ off!</p>
                    <p style="font-size: 14px;">""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
                </div>
        """
        
        for i, deal in enumerate(deals, 1):
            savings = deal['retail_price'] - deal['current_price']
            html += f"""
                <div class="deal">
                    <div class="deal-title">Deal #{i}: {deal['name']}</div>
                    <div class="price-info">
                        <span class="current-price">${deal['current_price']:.2f}</span>
                        <span class="retail-price"> was ${deal['retail_price']:.2f}</span>
                    </div>
                    <div style="margin: 10px 0;">
                        <span class="discount">{deal['discount_percent']:.1f}% OFF</span>
                        <span class="savings"> You save ${savings:.2f}!</span>
                    </div>
                    <a href="{deal['url']}" class="button">View Deal on Best Buy</a>
                </div>
            """
        
        html += """
                <div class="footer">
                    <p>This is an automated notification from your Best Buy Price Bot.</p>
                    <p>Act fast - deals may expire quickly!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

