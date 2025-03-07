# Ajwa Tech E-commerce Website

## 🚀 Overview
Ajwa Tech is a modern e-commerce website designed for selling electronics. Built using **Python, Django, PostgreSQL**, and the **HTML CSS**, the platform offers a seamless shopping experience with a secure and user-friendly interface. It is deployed on **AWS EC2** using **NGINX** as a reverse proxy.

## ✨ Features

### 🛍 User Side:
- **Cart & Wishlist** – Add and manage products easily.
- **Buy Now & Coupons** – Quick purchase and discount management.
- **Wallet & Multiple Payment Options** – Supports **Razorpay, Cash on Delivery (COD), and Wallet payments**.
- **User Profile & Order Management** – Track orders and update profile details.
- **Order History & Invoice Generation** – View past orders and download invoices.
- **Google & Facebook Authentication** – Secure social login integration.
- **Product Filtering & Sorting** – Find products efficiently with advanced filters.

### 🎛 Admin Side:
- **Admin Dashboard** – Monitor site activities and key metrics.
- **Product & User Management** – Add, edit, and manage products and users.
- **Order & Coupon Management** – Handle orders, apply discounts, and manage coupons.
- **Offer & Category Management** – Set product offers and categorize items effectively.
- **Sales Reports with Charts & Graphs** – **Chart.js** visualizations for better insights.
- **Downloadable Reports** – Export sales data in **PDF & Excel** format.

## 🔐 Security Features
- **Secure Payment Integration** – Supports **Razorpay** for seamless transactions.
- **OTP Authentication** – **Django send_mail** method for secure login verification.

## 🔧 Installation & Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/Ashkar-m/ajwa-tech.git
   ```
2. Navigate to the project directory:
   ```sh
   cd ajwa-tech
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up **PostgreSQL database** and update `settings.py` accordingly.
5. Run migrations:
   ```sh
   python manage.py migrate
   ```
6. Create a superuser for admin access:
   ```sh
   python manage.py createsuperuser
   ```
7. Start the server:
   ```sh
   python manage.py runserver
   ```
8. Deploy on **AWS EC2** and configure **NGINX** as a reverse proxy.

## 📌 Usage
- Users can browse, filter, and purchase electronic products.
- Admins can manage users, products, orders, and sales reports efficiently.

## 📫 Contact & Support
For any queries or contributions, feel free to reach out!

Happy shopping! 🛒🚀

