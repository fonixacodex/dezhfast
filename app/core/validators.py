import re

import dns.exception
import dns.resolver

# دامنه‌های معتبر
VALID_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "protonmail.com", "icloud.com", "live.com", "msn.com",
    "zoho.com", "yandex.com", "mail.com", "gmx.com",
}

# الگوی ایمیل
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def is_valid_email(email: str) -> tuple[bool, str]:
    """
    چک کن ایمیل معتبره.
    Returns: (valid, message)
    """
    # ۱. الگو
    if not EMAIL_PATTERN.match(email):
        return False, "فرمت ایمیل اشتباهه"
    
    local, domain = email.lower().split("@")
    
    # ۲. طول
    if len(local) < 2:
        return False, "نام ایمیل خیلی کوتاهه"
    
    # ۳. دامنه معتبر
    if domain not in VALID_DOMAINS:
        return False, "فقط ایمیل‌های معروف قبول می‌شن (Gmail, Yahoo, ...)"
    
    # ۴. MX record
    try:
        dns.resolver.resolve(domain, "MX", lifetime=3)
    except dns.exception.DNSException:
        return False, "دامنه‌ی ایمیل معتبر نیست"
    
    return True, ""


def is_disposable_email(email: str) -> bool:
    """چک کن ایمیل موقته."""
    domain = email.lower().split("@")[1]
    
    DISPOSABLE = {
        "tempmail.com", "guerrillamail.com", "10minutemail.com",
        "mailinator.com", "throwaway.email", "temp-mail.org",
        "fakeinbox.com", "sharklasers.com", "yopmail.com",
    }
    
    return domain in DISPOSABLE