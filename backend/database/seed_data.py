
from datetime import datetime
import random
from database.mongo_client import get_db

SIMULATED_PRODUCTS = [

    {
        "id": "SP001", "platform": "shopee",
        "name": "Samsung Galaxy A54 5G 128GB",
        "category": "dien-thoai", "category_name": "Điện thoại",
        "price": 7990000, "original_price": 9990000,
        "description": "Màn hình Super AMOLED 6.4 inch, camera 50MP OIS, pin 5000mAh, RAM 8GB, 5G",
        "brand": "Samsung", "stock": 45,
        "seller": {"name": "Samsung Official Store", "rating": 4.9, "response_rate": 98, "total_sales": 12500, "verified": True},
        "product_rating": 4.8, "review_count": 3200, "sold_count": 8900,
        "images": ["https://picsum.photos/seed/phone1/400/400"],
        "tags": ["samsung", "5g", "android", "camera", "gaming"],
        "specs": {"RAM": "8GB", "Storage": "128GB", "Display": "6.4 inch AMOLED", "Battery": "5000mAh", "Camera": "50MP"}
    },
    {
        "id": "TK001", "platform": "tiki",
        "name": "iPhone 15 128GB Chính Hãng VN/A",
        "category": "dien-thoai", "category_name": "Điện thoại",
        "price": 19990000, "original_price": 22990000,
        "description": "Chip A16 Bionic, camera 48MP Dynamic Island, USB-C, màu Pink/Blue/Yellow/Black/Green",
        "brand": "Apple", "stock": 28,
        "seller": {"name": "Tiki Trading", "rating": 4.8, "response_rate": 97, "total_sales": 45000, "verified": True},
        "product_rating": 4.9, "review_count": 8900, "sold_count": 15200,
        "images": ["https://picsum.photos/seed/iphone15/400/400"],
        "tags": ["iphone", "apple", "ios", "5g", "camera"],
        "specs": {"RAM": "6GB", "Storage": "128GB", "Display": "6.1 inch Super Retina XDR", "Battery": "3349mAh", "Camera": "48MP"}
    },
    {
        "id": "LZ001", "platform": "lazada",
        "name": "Xiaomi Redmi Note 13 Pro 256GB",
        "category": "dien-thoai", "category_name": "Điện thoại",
        "price": 6490000, "original_price": 7990000,
        "description": "Snapdragon 7s Gen 2, camera 200MP, sạc nhanh 67W, AMOLED 120Hz",
        "brand": "Xiaomi", "stock": 67,
        "seller": {"name": "Xiaomi Official", "rating": 4.7, "response_rate": 95, "total_sales": 9800, "verified": True},
        "product_rating": 4.6, "review_count": 1500, "sold_count": 4300,
        "images": ["https://picsum.photos/seed/xiaomi13/400/400"],
        "tags": ["xiaomi", "redmi", "android", "camera200mp", "sạcnhanh"],
        "specs": {"RAM": "8GB", "Storage": "256GB", "Display": "6.67 inch AMOLED 120Hz", "Battery": "5100mAh", "Camera": "200MP"}
    },
    {
        "id": "SP002", "platform": "shopee",
        "name": "OPPO Reno11 F 5G 256GB",
        "category": "dien-thoai", "category_name": "Điện thoại",
        "price": 7490000, "original_price": 8490000,
        "description": "MediaTek Dimensity 6080, camera selfie 32MP, pin 5000mAh, sạc SUPERVOOC 67W",
        "brand": "OPPO", "stock": 33,
        "seller": {"name": "OPPO Vietnam Official", "rating": 4.8, "response_rate": 96, "total_sales": 7600, "verified": True},
        "product_rating": 4.5, "review_count": 890, "sold_count": 2100,
        "images": ["https://picsum.photos/seed/opporeno11/400/400"],
        "tags": ["oppo", "5g", "selfie", "sạcnhanh"],
        "specs": {"RAM": "8GB", "Storage": "256GB", "Display": "6.7 inch AMOLED", "Battery": "5000mAh", "Camera": "64MP"}
    },

    {
        "id": "TK002", "platform": "tiki",
        "name": "Laptop ASUS VivoBook 15 OLED K3504VA",
        "category": "laptop", "category_name": "Laptop",
        "price": 18990000, "original_price": 22990000,
        "description": "Intel Core i5-1335U, RAM 16GB, SSD 512GB, màn hình OLED 15.6 inch 2.8K 120Hz",
        "brand": "ASUS", "stock": 15,
        "seller": {"name": "ASUS Store Vietnam", "rating": 4.8, "response_rate": 97, "total_sales": 6700, "verified": True},
        "product_rating": 4.7, "review_count": 654, "sold_count": 1890,
        "images": ["https://picsum.photos/seed/asusvivobook/400/400"],
        "tags": ["laptop", "asus", "oled", "intel", "sinh viên", "văn phòng"],
        "specs": {"CPU": "Intel Core i5-1335U", "RAM": "16GB DDR4", "Storage": "512GB SSD NVMe", "Display": "15.6 inch OLED 2.8K 120Hz", "Weight": "1.7kg"}
    },
    {
        "id": "LZ002", "platform": "lazada",
        "name": "MacBook Air M2 8GB 256GB 2022",
        "category": "laptop", "category_name": "Laptop",
        "price": 26990000, "original_price": 32990000,
        "description": "Apple M2 chip, RAM 8GB unified, SSD 256GB, màn hình Liquid Retina 13.6 inch, pin 18 giờ",
        "brand": "Apple", "stock": 12,
        "seller": {"name": "Apple Authorised Reseller", "rating": 4.9, "response_rate": 99, "total_sales": 23000, "verified": True},
        "product_rating": 4.9, "review_count": 4500, "sold_count": 8900,
        "images": ["https://picsum.photos/seed/macbookm2/400/400"],
        "tags": ["macbook", "apple", "m2", "macos", "mỏng nhẹ", "pin lâu"],
        "specs": {"CPU": "Apple M2", "RAM": "8GB Unified Memory", "Storage": "256GB SSD", "Display": "13.6 inch Liquid Retina", "Battery": "18 giờ"}
    },
    {
        "id": "SP003", "platform": "shopee",
        "name": "Laptop Dell Inspiron 15 3520 i5 Gen12",
        "category": "laptop", "category_name": "Laptop",
        "price": 14490000, "original_price": 16990000,
        "description": "Intel Core i5-1235U, RAM 8GB, SSD 512GB, FHD 120Hz, Windows 11 bản quyền",
        "brand": "Dell", "stock": 22,
        "seller": {"name": "Dell Official Shopee", "rating": 4.7, "response_rate": 94, "total_sales": 5400, "verified": True},
        "product_rating": 4.5, "review_count": 432, "sold_count": 1200,
        "images": ["https://picsum.photos/seed/dellinspiro/400/400"],
        "tags": ["laptop", "dell", "intel", "windows11", "sinh viên"],
        "specs": {"CPU": "Intel Core i5-1235U", "RAM": "8GB DDR4", "Storage": "512GB SSD", "Display": "15.6 inch FHD 120Hz", "Weight": "1.89kg"}
    },

    {
        "id": "SP004", "platform": "shopee",
        "name": "Sony WH-1000XM5 Tai nghe chống ồn",
        "category": "tai-nghe", "category_name": "Tai nghe",
        "price": 6990000, "original_price": 9990000,
        "description": "Chống ồn chủ động ANC hàng đầu, pin 30 giờ, kết nối Bluetooth 5.2, LDAC Hi-Res",
        "brand": "Sony", "stock": 28,
        "seller": {"name": "Sony Vietnam Official", "rating": 4.9, "response_rate": 98, "total_sales": 11200, "verified": True},
        "product_rating": 4.9, "review_count": 2800, "sold_count": 6700,
        "images": ["https://picsum.photos/seed/sonywh1000/400/400"],
        "tags": ["tai nghe", "sony", "chống ồn", "anc", "bluetooth", "âm nhạc"],
        "specs": {"Driver": "30mm", "Frequency": "4Hz-40kHz", "Battery": "30 giờ", "Connectivity": "Bluetooth 5.2", "Weight": "250g"}
    },
    {
        "id": "TK003", "platform": "tiki",
        "name": "Tai nghe True Wireless Samsung Galaxy Buds2 Pro",
        "category": "tai-nghe", "category_name": "Tai nghe",
        "price": 3290000, "original_price": 4490000,
        "description": "ANC 2 chiều, âm thanh 24bit Hi-Fi, pin 5 giờ + 13 giờ hộp sạc, IPX7",
        "brand": "Samsung", "stock": 54,
        "seller": {"name": "Samsung Official Store Tiki", "rating": 4.8, "response_rate": 97, "total_sales": 8900, "verified": True},
        "product_rating": 4.7, "review_count": 1890, "sold_count": 4500,
        "images": ["https://picsum.photos/seed/samsungbuds2/400/400"],
        "tags": ["tai nghe", "samsung", "true wireless", "anc", "ipx7"],
        "specs": {"Driver": "10.5mm + 6.1mm", "Battery": "5h + 13h", "Connectivity": "Bluetooth 5.3", "Weight": "5.5g/tai", "Water resistance": "IPX7"}
    },
    {
        "id": "LZ003", "platform": "lazada",
        "name": "Tai nghe JBL Tune 770NC Bluetooth",
        "category": "tai-nghe", "category_name": "Tai nghe",
        "price": 1890000, "original_price": 2490000,
        "description": "ANC chủ động, pin 70 giờ không ANC / 44 giờ có ANC, âm thanh Pure Bass",
        "brand": "JBL", "stock": 78,
        "seller": {"name": "JBL Official Lazada", "rating": 4.6, "response_rate": 93, "total_sales": 6700, "verified": True},
        "product_rating": 4.5, "review_count": 1200, "sold_count": 3400,
        "images": ["https://picsum.photos/seed/jbl770/400/400"],
        "tags": ["tai nghe", "jbl", "anc", "pin lâu", "bass"],
        "specs": {"Battery": "70 giờ (không ANC)", "Connectivity": "Bluetooth 5.3", "Driver": "40mm", "Weight": "222g", "Foldable": "Có"}
    },

    {
        "id": "SP005", "platform": "shopee",
        "name": "Nồi chiên không dầu Philips HD9270 6.2L",
        "category": "gia-dung", "category_name": "Gia dụng",
        "price": 2890000, "original_price": 3890000,
        "description": "Công nghệ Rapid Air 2.0, dung tích 6.2L, công suất 1725W, cảm ứng, 7 preset chương trình",
        "brand": "Philips", "stock": 43,
        "seller": {"name": "Philips Official VN", "rating": 4.8, "response_rate": 96, "total_sales": 14500, "verified": True},
        "product_rating": 4.8, "review_count": 5600, "sold_count": 12000,
        "images": ["https://picsum.photos/seed/philipsAF/400/400"],
        "tags": ["nồi chiên", "philips", "không dầu", "gia dụng", "nấu ăn"],
        "specs": {"Capacity": "6.2L", "Power": "1725W", "Temperature": "40-200°C", "Timer": "60 phút", "Weight": "5.8kg"}
    },
    {
        "id": "TK004", "platform": "tiki",
        "name": "Máy xay sinh tố Vitamix E310 Explorian",
        "category": "gia-dung", "category_name": "Gia dụng",
        "price": 8990000, "original_price": 11990000,
        "description": "Motor 1380W, hũ 1.4L Tritan không BPA, 10 tốc độ + chế độ xung, bảo hành 5 năm",
        "brand": "Vitamix", "stock": 8,
        "seller": {"name": "Vitamix Vietnam", "rating": 4.9, "response_rate": 98, "total_sales": 3200, "verified": True},
        "product_rating": 4.9, "review_count": 890, "sold_count": 2100,
        "images": ["https://picsum.photos/seed/vitamix/400/400"],
        "tags": ["máy xay", "vitamix", "sinh tố", "gia dụng", "cao cấp"],
        "specs": {"Power": "1380W", "Capacity": "1.4L", "Speed": "10 levels + Pulse", "Warranty": "5 năm", "BPA Free": "Có"}
    },

    {
        "id": "SP006", "platform": "shopee",
        "name": "Giày Nike Air Max 270 Nam Original",
        "category": "giay-dep", "category_name": "Giày dép",
        "price": 3290000, "original_price": 4390000,
        "description": "Đế Max Air 270° lớn nhất lịch sử Nike, mesh thoáng khí, đế foam phản lực cao",
        "brand": "Nike", "stock": 65,
        "seller": {"name": "Nike Vietnam Official", "rating": 4.8, "response_rate": 97, "total_sales": 28900, "verified": True},
        "product_rating": 4.7, "review_count": 6700, "sold_count": 18000,
        "images": ["https://picsum.photos/seed/nikeam270/400/400"],
        "tags": ["giày", "nike", "air max", "thể thao", "nam"],
        "specs": {"Material": "Mesh + tổng hợp", "Sole": "Max Air + React foam", "Closure": "Dây buộc", "Gender": "Nam", "Style": "Lifestyle"}
    },
    {
        "id": "LZ004", "platform": "lazada",
        "name": "Áo Polo Lacoste Regular Fit Cotton Piqué",
        "category": "thoi-trang-nam", "category_name": "Thời trang nam",
        "price": 1890000, "original_price": 2490000,
        "description": "Cotton piqué 100%, cổ bẻ 2 nút, logo cá sấu thêu, phong cách classic",
        "brand": "Lacoste", "stock": 89,
        "seller": {"name": "Lacoste Official Lazada", "rating": 4.7, "response_rate": 95, "total_sales": 12300, "verified": True},
        "product_rating": 4.6, "review_count": 2300, "sold_count": 5600,
        "images": ["https://picsum.photos/seed/lacoste/400/400"],
        "tags": ["áo polo", "lacoste", "thời trang nam", "cotton", "classic"],
        "specs": {"Material": "100% Cotton Piqué", "Fit": "Regular Fit", "Collar": "Bẻ 2 nút", "Care": "Machine wash 30°C", "Origin": "Pháp"}
    },

    {
        "id": "TK005", "platform": "tiki",
        "name": "Kem chống nắng Anessa Perfect UV Sunscreen SPF50+ PA++++",
        "category": "my-pham", "category_name": "Mỹ phẩm",
        "price": 425000, "original_price": 520000,
        "description": "SPF50+ PA++++, công nghệ Aqua Booster EX bền nước mồ hôi, phù hợp mọi loại da",
        "brand": "Anessa", "stock": 234,
        "seller": {"name": "Shiseido Vietnam Official", "rating": 4.9, "response_rate": 99, "total_sales": 89000, "verified": True},
        "product_rating": 4.8, "review_count": 23000, "sold_count": 67000,
        "images": ["https://picsum.photos/seed/anessa/400/400"],
        "tags": ["kem chống nắng", "anessa", "spf50", "mỹ phẩm", "nhật"],
        "specs": {"SPF": "50+", "PA": "++++", "Volume": "60ml", "Skin type": "Mọi loại da", "Water resistant": "Có"}
    },
    {
        "id": "SP007", "platform": "shopee",
        "name": "Serum Vitamin C Paula's Choice 20% Vitamin C + E Ferulic",
        "category": "my-pham", "category_name": "Mỹ phẩm",
        "price": 890000, "original_price": 1190000,
        "description": "20% Vitamin C thuần, Vitamin E, Ferulic Acid chống oxy hóa, làm sáng và đều màu da",
        "brand": "Paula's Choice", "stock": 56,
        "seller": {"name": "Paula's Choice Vietnam", "rating": 4.8, "response_rate": 97, "total_sales": 34000, "verified": True},
        "product_rating": 4.7, "review_count": 8900, "sold_count": 23000,
        "images": ["https://picsum.photos/seed/paulaschoice/400/400"],
        "tags": ["serum", "vitamin c", "paula's choice", "mỹ phẩm", "dưỡng da"],
        "specs": {"Vitamin C": "20%", "Volume": "30ml", "Skin type": "Mọi loại da", "Usage": "Buổi sáng", "Key ingredients": "Vitamin C, E, Ferulic"}
    },

    {
        "id": "TK006", "platform": "tiki",
        "name": "Đắc Nhân Tâm - Dale Carnegie (Bìa Cứng)",
        "category": "sach", "category_name": "Sách",
        "price": 89000, "original_price": 120000,
        "description": "Cuốn sách bán chạy nhất mọi thời đại về kỹ năng giao tiếp và tạo dựng mối quan hệ",
        "brand": "NXB Tổng hợp TP.HCM", "stock": 456,
        "seller": {"name": "Tiki Trading", "rating": 4.9, "response_rate": 99, "total_sales": 234000, "verified": True},
        "product_rating": 4.9, "review_count": 45000, "sold_count": 120000,
        "images": ["https://picsum.photos/seed/dacnantam/400/400"],
        "tags": ["sách", "kỹ năng", "dale carnegie", "giao tiếp", "bestseller"],
        "specs": {"Pages": "320 trang", "Publisher": "NXB Tổng hợp TP.HCM", "Language": "Tiếng Việt", "Cover": "Bìa cứng", "Translator": "Nguyễn Văn Phước"}
    },

    {
        "id": "LZ005", "platform": "lazada",
        "name": "Đồng hồ thông minh Samsung Galaxy Watch6 Classic 47mm",
        "category": "dong-ho-thong-minh", "category_name": "Đồng hồ thông minh",
        "price": 7490000, "original_price": 9990000,
        "description": "Vòng bezel xoay vật lý, theo dõi sức khỏe 24/7, ECG, huyết áp, Wear OS 4",
        "brand": "Samsung", "stock": 18,
        "seller": {"name": "Samsung Official Lazada", "rating": 4.8, "response_rate": 96, "total_sales": 15600, "verified": True},
        "product_rating": 4.7, "review_count": 2100, "sold_count": 5400,
        "images": ["https://picsum.photos/seed/galaxywatch6/400/400"],
        "tags": ["smartwatch", "samsung", "galaxy watch", "sức khỏe", "ecg"],
        "specs": {"Display": "1.5 inch Super AMOLED", "Battery": "425mAh / ~40 giờ", "OS": "Wear OS 4", "Water resistance": "5ATM + IP68", "Health": "ECG, huyết áp, SpO2"}
    },
    {
        "id": "SP008", "platform": "shopee",
        "name": "Apple Watch Series 9 GPS 41mm Midnight",
        "category": "dong-ho-thong-minh", "category_name": "Đồng hồ thông minh",
        "price": 9990000, "original_price": 12990000,
        "description": "Chip S9 SiP, Double Tap gesture, màn sáng 2000 nits, carbon neutral, theo dõi sức khỏe toàn diện",
        "brand": "Apple", "stock": 23,
        "seller": {"name": "Apple Reseller Shopee", "rating": 4.8, "response_rate": 97, "total_sales": 19800, "verified": True},
        "product_rating": 4.8, "review_count": 3400, "sold_count": 8900,
        "images": ["https://picsum.photos/seed/applewatch9/400/400"],
        "tags": ["apple watch", "smartwatch", "ios", "sức khỏe", "watchos"],
        "specs": {"Chip": "S9 SiP", "Display": "Always-On Retina LTPO OLED", "Battery": "~18 giờ", "Water resistance": "50m WR", "Health": "ECG, SpO2, nhiệt độ da"}
    },

    {
        "id": "TK007", "platform": "tiki",
        "name": "Chuột không dây Logitech MX Master 3S",
        "category": "phu-kien-may-tinh", "category_name": "Phụ kiện máy tính",
        "price": 1890000, "original_price": 2390000,
        "description": "8K DPI MagSpeed scroll, silent click, đa thiết bị, USB-C, pin 70 ngày, ergonomic cao cấp",
        "brand": "Logitech", "stock": 67,
        "seller": {"name": "Logitech Official Tiki", "rating": 4.8, "response_rate": 97, "total_sales": 23400, "verified": True},
        "product_rating": 4.8, "review_count": 4500, "sold_count": 11200,
        "images": ["https://picsum.photos/seed/mxmaster3s/400/400"],
        "tags": ["chuột", "logitech", "mx master", "không dây", "ergonomic", "làm việc"],
        "specs": {"DPI": "200-8000 DPI", "Battery": "70 ngày", "Connectivity": "Bluetooth + Logi Bolt", "Buttons": "7 nút", "Charging": "USB-C"}
    },

    {
        "id": "SP009", "platform": "shopee",
        "name": "Cà phê rang xay Trung Nguyên E-Coffee Số 1 1kg",
        "category": "thuc-pham", "category_name": "Thực phẩm",
        "price": 165000, "original_price": 195000,
        "description": "Blend đặc biệt Robusta + Arabica, rang medium, hương thơm đặc trưng miền Nam Việt Nam",
        "brand": "Trung Nguyên", "stock": 892,
        "seller": {"name": "Trung Nguyen Official", "rating": 4.7, "response_rate": 95, "total_sales": 145000, "verified": True},
        "product_rating": 4.6, "review_count": 23400, "sold_count": 89000,
        "images": ["https://picsum.photos/seed/trungnguyen/400/400"],
        "tags": ["cà phê", "trung nguyên", "rang xay", "thực phẩm", "việt nam"],
        "specs": {"Weight": "1kg", "Blend": "Robusta + Arabica", "Roast": "Medium", "Origin": "Tây Nguyên, Việt Nam", "Grind": "Xay vừa"}
    }
]

def seed_database():
    from database.mongo_client import get_db, is_connected
    db = get_db()
    if db is None:
        print("No MongoDB connection - seed skipped (will use in-memory data)")
        return False
    try:
        if db.products.count_documents({}) == 0:
            db.products.insert_many(SIMULATED_PRODUCTS)
            print(f"Seeded {len(SIMULATED_PRODUCTS)} products")
        else:
            print(f"Products already seeded ({db.products.count_documents({})} total)")
        return True
    except Exception as e:
        print(f"Seed error: {e}")
        return False

def get_all_products():
    """Fallback: return in-memory products when MongoDB unavailable"""
    return SIMULATED_PRODUCTS