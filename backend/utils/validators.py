
import re
import html
from typing import Tuple


SCRIPT_INJECTION_PATTERNS = [
    r'<script[^>]*>', r'</script>', r'javascript:', r'on\w+\s*=',
    r'<iframe', r'<object', r'<embed', r'<link', r'<meta',
    r'document\.cookie', r'window\.location', r'eval\(',
    r'fetch\(', r'XMLHttpRequest', r'\.php\?', r'SELECT\s+\*',
    r'DROP\s+TABLE', r'INSERT\s+INTO', r'UNION\s+SELECT',
    r'\.\./\.\.', r'%2e%2e', r'curl\s', r'wget\s',
]

OFF_TOPIC_PATTERNS = [
    r'\b(thời tiết|hôm nay nắng|hôm nay mưa|trời)\b',
    r'\b(tôi buồn|tôi vui|tôi khóc|tôi đau|tôi mệt|tâm sự|chia sẻ cảm xúc)\b',
    r'\b(bài thơ|kể chuyện|viết truyện|sáng tác)\b',
    r'\b(toán học|tính toán|phương trình|code|lập trình)\b',
    r'\b(nấu ăn công thức|dạy nấu|học nấu)\b',
    r'\b(dịch thuật|translate|hỏi về lịch sử|địa lý)\b',
]

SENSITIVE_CONTENT_PATTERNS = [

    r'\b(chính trị|đảng phái|bầu cử|cách mạng|lật đổ|chế độ|chính quyền|tổng thống|chủ tịch nước)\b',

    r'\b(tôn giáo|đạo phật|thiên chúa|hồi giáo|tin lành|thờ cúng|kinh thánh|kinh koran)\b',

    r'\b(bạo lực|giết người|đánh nhau|khủng bố|chiến tranh|vũ khí|súng)\b',

    r'\b(sex|khiêu dâm|18\+|người lớn|porn)\b',
]

SUSPICIOUS_CHARS = r'[<>\{\}\[\]\\|`\^~]'

def sanitize_input(text: str) -> str:
    if not text:
        return ""
    text = html.escape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.strip()[:1000]  
    return text

def validate_user_input(text: str) -> Tuple[bool, str]:

    if not text or not text.strip():
        return False, "Vui lòng nhập yêu cầu của bạn."
    
    if len(text) > 1000:
        return False, "Yêu cầu quá dài. Vui lòng nhập tối đa 1000 ký tự."

    text_lower = text.lower()
    for pattern in SCRIPT_INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False, "Yêu cầu chứa nội dung không hợp lệ. Vui lòng chỉ hỏi về sản phẩm mua sắm."

    # Suspicious special characters
    suspicious_count = len(re.findall(SUSPICIOUS_CHARS, text))
    if suspicious_count > 5:
        return False, "Yêu cầu chứa ký tự đặc biệt không hợp lệ."

    for pattern in SENSITIVE_CONTENT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "Tôi chỉ hỗ trợ tư vấn mua sắm sản phẩm. Câu hỏi của bạn không thuộc phạm vi này."

    for pattern in OFF_TOPIC_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "Tôi là trợ lý mua sắm! Tôi chỉ có thể giúp bạn tìm kiếm và tư vấn sản phẩm. Bạn muốn mua gì hôm nay?"

    return True, ""

def validate_product_content(product: dict) -> bool:
    sensitive_keywords = [
        'chính trị', 'tôn giáo', 'bạo lực', 'kích động', 'đảng',
        'súng', 'vũ khí', 'khủng bố', '18+', 'người lớn'
    ]
    text = f"{product.get('name', '')} {product.get('description', '')}".lower()
    for kw in sensitive_keywords:
        if kw in text:
            return False
    return True

def extract_price_from_text(text: str) -> dict:

    price_info = {"min": None, "max": None}

    text_lower = text.lower()

    under_patterns = [
        r'(?:dưới|không quá|tối đa|max|under|bé hơn|nhỏ hơn)\s*(\d+(?:[.,]\d+)?)\s*(?:triệu|tr|million|m\b)',
        r'(?:dưới|không quá|tối đa)\s*(\d+(?:[.,]\d+)?)\s*(?:nghìn|k\b)',
        r'(?:dưới|không quá|tối đa)\s*(\d{4,})\s*(?:đ|vnd|vnđ)?',
    ]
    
    for p in under_patterns:
        m = re.search(p, text_lower)
        if m:
            val = float(m.group(1).replace(',', '.'))
            if 'nghìn' in p or 'k' in p:
                price_info['max'] = int(val * 1000)
            elif 'triệu' in p or 'tr' in p or 'million' in p:
                price_info['max'] = int(val * 1_000_000)
            else:
                price_info['max'] = int(val)
            break

    over_patterns = [
        r'(?:trên|từ|hơn|ít nhất|min)\s*(\d+(?:[.,]\d+)?)\s*(?:triệu|tr|million)',
        r'(?:trên|từ|hơn)\s*(\d+(?:[.,]\d+)?)\s*(?:nghìn|k\b)',
    ]
    for p in over_patterns:
        m = re.search(p, text_lower)
        if m:
            val = float(m.group(1).replace(',', '.'))
            if 'nghìn' in p or 'k' in p:
                price_info['min'] = int(val * 1000)
            else:
                price_info['min'] = int(val * 1_000_000)
            break

    if price_info['max'] is None and price_info['min'] is None:
        m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:triệu|tr\b)', text_lower)
        if m:
            val = float(m.group(1).replace(',', '.'))
            price_info['max'] = int(val * 1_000_000)

    if price_info['max'] is None:
        m = re.search(r'(\d+)\s*k\b', text_lower)
        if m:
            price_info['max'] = int(m.group(1)) * 1000

    return price_info