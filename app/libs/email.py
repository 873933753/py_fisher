import logging
import smtplib
from email.message import EmailMessage

from app.libs.templates import templates
from app.secure import MAIL_USERNAME, MAIL_PASSWORD, MAIL_SERVER, MAIL_PORT, MAIL_SENDER

logger = logging.getLogger(__name__)


def send_email(
    to: str,
    subject: str,
    template: str,
    # 动态参数,用于传递模板中的变量
    **kwargs,
):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_SENDER
    msg["To"] = to

    # jinja2渲染模板
    html = templates.get_template(template).render(**kwargs)
    msg.set_content(html, subtype="html")

    with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT) as server:
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)


def send_email_safe(to: str, subject: str, template: str, **kwargs):
    try:
        send_email(to=to, subject=subject, template=template, **kwargs)
    except Exception:
        logger.exception("发送邮件失败: to=%s subject=%s", to, subject)
