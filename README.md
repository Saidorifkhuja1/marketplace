# Django Marketplace API

A modern, production-ready Django REST Framework API for a peer-to-peer marketplace with Telegram bot integration, real-time messaging, and comprehensive product management.

## 🚀 Features

### Core Functionality
- **User Management**: Custom authentication with phone/email, role-based access (seller/client)
- **Product Listings**: Multi-photo support (up to 5 images), categories, status tracking
- **Shopping Cart**: Add/remove products, cart management
- **Messaging System**: Real-time chat between users with read status
- **Product Reviews**: Comment and rating system
- **Advanced Filtering**: Search and filter products by category, price, location

### Telegram Integration
- **Seamless Login**: HMAC-SHA256 secured Telegram WebApp authentication
- **Bot Commands**: Start command with automatic user registration
- **Mini App Support**: Ready for Telegram mini-app deployment

### API Features
- **JWT Authentication**: Secure token-based authentication with 1000-week expiry
- **API Documentation**: Swagger/OpenAPI and ReDoc available
- **CORS Support**: Configurable cross-origin resource sharing
- **Pagination**: Limit-offset pagination (10 items per page)
- **Filtering & Search**: Django filters with full-text search

### Admin Interface
- **Jazzmin Admin**: Modern, user-friendly Django admin panel
- **Product Management**: Approve/reject pending products
- **User Management**: View and manage users and roles

## 🛠 Tech Stack

- **Backend**: Django 5.2.4 with Django REST Framework 3.16.0
- **Database**: PostgreSQL 15 (SQLite for development)
- **Authentication**: JWT (djangorestframework_simplejwt)
- **Bot**: Aiogram 3.21.0 (Telegram bot framework)
- **Web Server**: Gunicorn + Nginx
- **Containerization**: Docker & Docker Compose
- **API Docs**: drf-yasg (Swagger/OpenAPI)
- **Admin**: Django Jazzmin 3.0.1

## 📋 Project Structure

```
marketplace/
├── core/                    # Django project settings
│   ├── settings.py         # Configuration
│   ├── urls.py             # URL routing
│   ├── wsgi.py             # WSGI application
│   └── asgi.py             # ASGI application
├── user/                    # User authentication & profiles
│   ├── models.py           # User model with custom auth
│   ├── views.py            # Authentication endpoints
│   ├── serializers.py      # User serializers
│   ├── telegram_auth.py    # Telegram auth logic
│   └── urls.py             # User routes
├── product/                 # Product management
│   ├── models.py           # Product & Category models
│   ├── views.py            # Product CRUD endpoints
│   ├── serializers.py      # Product serializers
│   └── urls.py             # Product routes
├── cart/                    # Shopping cart
│   ├── models.py           # Cart model
│   ├── views.py            # Cart endpoints
│   └── urls.py             # Cart routes
├── comment/                 # Product reviews
│   ├── models.py           # Comment model
│   ├── views.py            # Comment endpoints
│   └── urls.py             # Comment routes
├── message/                 # Messaging system
│   ├── models.py           # Chat & Message models
│   ├── views.py            # Messaging endpoints
│   ├── serializers.py      # Message serializers
│   └── urls.py             # Message routes
├── filters/                 # Product filtering
│   ├── views.py            # Filter endpoints
│   └── urls.py             # Filter routes
├── tg_bot/                  # Telegram bot
│   ├── bot.py              # Bot handlers & logic
│   └── tokens.py           # Bot token configuration
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Multi-container setup
├── nginx.conf              # Nginx reverse proxy config
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
├── DEPLOYMENT.md           # Deployment guide
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (for production)

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd marketplace
```

2. **Create environment file**
```bash
cp .envexample .env
```

3. **Build and run with Docker**
```bash
docker-compose up -d
```

4. **Run migrations**
```bash
docker-compose exec web python manage.py migrate
```

5. **Create superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

6. **Access the application**
- API: http://localhost:8000
- Admin: http://localhost:8000/admin
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Local Development (Without Docker)

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure database** (SQLite for development)
```bash
# Edit .env or use defaults
python manage.py migrate
```

4. **Create superuser**
```bash
python manage.py createsuperuser
```

5. **Run development server**
```bash
python manage.py runserver
```

## 📚 API Documentation

### Authentication

All protected endpoints require JWT token in Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

### Key Endpoints

#### User Management
- `POST /user/register/` - Register new user
- `POST /user/telegram/login/` - Telegram login
- `GET /user/profile/` - Get user profile
- `PUT /user/profile/` - Update profile

#### Products
- `GET /product/` - List products
- `POST /product/` - Create product
- `GET /product/{id}/` - Get product details
- `PUT /product/{id}/` - Update product
- `DELETE /product/{id}/` - Delete product

#### Cart
- `GET /cart/` - View cart
- `POST /cart/` - Add to cart
- `DELETE /cart/{id}/` - Remove from cart

#### Messages
- `GET /message/chats/` - List chats
- `POST /message/send/` - Send message
- `GET /message/chats/{chat_id}/messages/` - Get chat messages

#### Comments
- `GET /comment/` - List comments
- `POST /comment/` - Create comment
- `DELETE /comment/{id}/` - Delete comment

### Full API Documentation

Visit `/docs` or `/redoc` after starting the server for interactive API documentation.

## 🔐 Environment Variables

See `.env.example` for all available options. Key variables:

```env
# Django
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=marketplace
DB_USER=marketplace_user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token

# CORS
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access shell
docker-compose exec web bash

# Database shell
docker-compose exec db psql -U marketplace_user -d marketplace
```

## 📦 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide including:
- Production environment setup
- SSL/TLS configuration
- Database backups
- Monitoring and logging
- Troubleshooting

Quick deployment:

```bash
# On your server
git clone <repository-url>
cd marketplace
cp .envexample .env
# Edit .env with production values
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## 🧪 Testing

```bash
# Run tests
docker-compose exec web python manage.py test

# Run specific app tests
docker-compose exec web python manage.py test user

# With coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

## 📊 Database Schema

### User Model
- `uid` (UUID): Primary key
- `email` (Email): Unique, required
- `name` (String): User's full name
- `phone_number` (String): Uzbek format validation
- `telegram_id` (BigInt): Unique Telegram ID
- `role` (Choice): 'seller' or 'client'
- `photo` (Image): Profile picture
- `is_active` (Boolean): Account status
- `created_at` (DateTime): Creation timestamp

### Product Model
- `uid` (UUID): Primary key
- `name` (String): Product name
- `description` (Text): Product details
- `cost` (Decimal): Price
- `amount` (Integer): Quantity available
- `owner` (FK): Product owner (User)
- `category` (FK): Product category
- `status` (Choice): 'pending', 'active', 'sold_out'
- `location` (String): Product location
- `photo1-5` (Image): Product images (up to 5)
- `created_at` (DateTime): Creation timestamp

### Message Model
- `uid` (UUID): Primary key
- `chat` (FK): Chat conversation
- `sender` (FK): Message sender (User)
- `receiver` (FK): Message receiver (User)
- `content` (Text): Message content
- `is_read` (Boolean): Read status
- `created_at` (DateTime): Creation timestamp

## 🔄 Telegram Bot Integration

### Setup

1. Create bot with BotFather: `/newbot`
2. Get bot token
3. Create `tg_bot/tokens.py`:
```python
BOT_TOKEN = "your-bot-token-here"
```

4. Set in `.env`:
```env
TELEGRAM_BOT_TOKEN=your-bot-token
```

### Usage

Users can:
1. Start bot with `/start`
2. Bot generates secure auth hash
3. User gets JWT token
4. Mini app opens with authenticated session

## 🛡️ Security

- JWT token-based authentication
- HMAC-SHA256 Telegram verification
- CORS configuration
- SQL injection protection (Django ORM)
- CSRF protection
- Password hashing with Django's default algorithm
- Environment-based secrets management

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📞 Support

For issues, questions, or suggestions:
1. Check existing issues
2. Review documentation
3. Create new issue with detailed description

## 🎯 Roadmap

- [ ] Frontend (React/Vue)
- [ ] Payment integration (Stripe/PayPal)
- [ ] Order management system
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Advanced analytics
- [ ] Mobile app
- [ ] WebSocket support for real-time messaging
- [ ] Image optimization and CDN integration
- [ ] Rate limiting and throttling

## 📚 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Aiogram Documentation](https://docs.aiogram.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Made with ❤️ for the marketplace community**
