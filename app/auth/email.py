"""
Email Service Module

This module handles all email-related functionality for the application:
- Email verification for new users
- Password reset emails
- Welcome emails
- Notification emails

Uses SMTP for sending emails with HTML templates.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime, timedelta, timezone
import secrets
from app.core.config import get_settings

settings = get_settings()


class EmailService:
    """Email service for sending various types of emails."""
    
    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from = settings.SMTP_FROM
        self.app_name = settings.APP_NAME
        
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text alternative (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text part
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            # Add HTML part
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def send_verification_email(
        self,
        to_email: str,
        username: str,
        verification_token: str,
        base_url: str
    ) -> bool:
        """
        Send email verification link to user.
        
        Args:
            to_email: User's email address
            username: User's username
            verification_token: Verification token
            base_url: Base URL of the application
            
        Returns:
            bool: True if email sent successfully
        """
        verification_link = f"{base_url}/api/auth/verify-email?token={verification_token}"
        
        subject = f"Verify your {self.app_name} account"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #4CAF50;
                    margin: 0;
                }}
                .content {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .button:hover {{
                    background-color: #45a049;
                }}
                .footer {{
                    text-align: center;
                    color: #777;
                    font-size: 12px;
                    margin-top: 20px;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 10px;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{self.app_name}</h1>
                    <p>Email Verification</p>
                </div>
                
                <div class="content">
                    <h2>Welcome, {username}! 👋</h2>
                    
                    <p>Thank you for registering with {self.app_name}. To complete your registration and start using your account, please verify your email address.</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_link}" class="button">Verify Email Address</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666; font-size: 12px;">
                        {verification_link}
                    </p>
                    
                    <div class="warning">
                        <strong>⏱️ Important:</strong> This verification link will expire in 24 hours for security reasons.
                    </div>
                </div>
                
                <div class="footer">
                    <p>If you didn't create an account with {self.app_name}, please ignore this email.</p>
                    <p>© {datetime.now().year} {self.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to {self.app_name}, {username}!
        
        Please verify your email address by clicking the link below:
        {verification_link}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        """
        
        return self._send_email(to_email, subject, html_content, text_content)
    
    def send_welcome_email(
        self,
        to_email: str,
        username: str,
        first_name: str
    ) -> bool:
        """
        Send welcome email after successful verification.
        
        Args:
            to_email: User's email address
            username: User's username
            first_name: User's first name
            
        Returns:
            bool: True if email sent successfully
        """
        subject = f"Welcome to {self.app_name}!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #4CAF50;
                    margin: 0;
                }}
                .content {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .footer {{
                    text-align: center;
                    color: #777;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to {self.app_name}!</h1>
                </div>
                
                <div class="content">
                    <h2>Hello, {first_name}! 👋</h2>
                    
                    <p>Your email has been verified successfully! You can now access all features of {self.app_name}.</p>
                    
                    <h3>Getting Started:</h3>
                    <ul>
                        <li>Create your first calculation</li>
                        <li>Explore the dashboard</li>
                        <li>Customize your profile</li>
                    </ul>
                    
                    <p>If you have any questions or need assistance, feel free to reach out to our support team.</p>
                </div>
                
                <div class="footer">
                    <p>© {datetime.now().year} {self.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to {self.app_name}, {first_name}!
        
        Your email has been verified successfully!
        
        You can now access all features of {self.app_name}.
        """
        
        return self._send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_email(
        self,
        to_email: str,
        username: str,
        reset_token: str,
        base_url: str
    ) -> bool:
        """
        Send password reset email.
        
        Args:
            to_email: User's email address
            username: User's username
            reset_token: Password reset token
            base_url: Base URL of the application
            
        Returns:
            bool: True if email sent successfully
        """
        reset_link = f"{base_url}/reset-password?token={reset_token}"
        
        subject = f"{self.app_name} - Password Reset Request"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .content {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #f44336;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .warning {{
                    background-color: #ffebee;
                    border-left: 4px solid #f44336;
                    padding: 10px;
                    margin: 15px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #777;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{self.app_name}</h1>
                    <p>Password Reset Request</p>
                </div>
                
                <div class="content">
                    <h2>Hello, {username}! 🔐</h2>
                    
                    <p>We received a request to reset your password. Click the button below to create a new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666; font-size: 12px;">
                        {reset_link}
                    </p>
                    
                    <div class="warning">
                        <strong>⏱️ Important:</strong> This link will expire in 1 hour for security reasons.
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>Didn't request this?</strong> You can safely ignore this email. Your password will not be changed.</p>
                    <p>© {datetime.now().year} {self.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request - {self.app_name}
        
        Hello {username},
        
        We received a request to reset your password. Click the link below:
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email.
        """
        
        return self._send_email(to_email, subject, html_content, text_content)


# Singleton instance
email_service = EmailService()
