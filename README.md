# Cấu trúc

ecommerce-chatbot/
├── backend/
│   ├── app.py                  # Entry point Flask
│   ├── api/
│   │   ├── chat_routes.py      # API chat /api/chat/*
│   │   ├── product_routes.py   # API sản phẩm /api/products/*
│   │   └── analytics_routes.py # API thống kê /api/analytics/*
│   ├── services/
│   │   ├── ai_service.py       # Gọi Claude API, xử lý response
│   │   ├── product_service.py  # Tìm kiếm, lọc, xếp hạng sản phẩm
│   │   └── session_service.py  # Quản lý phiên, lưu lịch sử, analytics
│   ├── database/
│   │   ├── mongo_client.py     # Kết nối MongoDB
│   │   └── seed_data.py        # Dữ liệu mô phỏng 19 sản phẩm
│   └── utils/
│       └── validators.py       # Validate input, lọc nội dung, trích giá
├── frontend/
│   ├── templates/
│   │   ├── index.html          # Giao diện chat chính
│   │   ├── product_detail.html # Trang chi tiết sản phẩm
│   │   └── analytics.html      # Dashboard thống kê
│   └── static/
│       ├── css/
│       │   ├── main.css        # Stylesheet chính (dark mode)
│       │   ├── product_detail.css
│       │   └── analytics.css
│       └── js/
│           ├── utils.js        # Tiện ích chung
│           ├── chat.js         # Module chat
│           ├── products.js     # Module hiển thị sản phẩm
│           ├── main.js         # Event wiring
│           ├── product_detail.js
│           └── analytics.js
├── requirements.txt
├── .env.example
└── README.md

### Hướng dẫn sử dụng

# 1. Cài đặt dependencies

bash
cd ecommerce-chatbot
pip install -r requirements.txt

# 2. Cấu hình môi trường

bash
cp .env.example .env
# Mở .env và điền ANTHROPIC_API_KEY


# 3. (Tuỳ chọn) Cài đặt MongoDB

bash
# Ubuntu/Debian
sudo apt install mongodb
sudo systemctl start mongodb

# Nếu không có MongoDB, hệ thống sẽ tự dùng in-memory storage


# 4. Chạy server

bash
cd backend
python app.py

Truy cập: **http://localhost:5000**



# ChatBot_AI_Conversational-Shopping-Assistant-with-E-commerce-Data-Analytics
