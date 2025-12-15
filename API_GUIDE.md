# 🔐 REST API with JWT Authentication & Email Verification

## Overview

This is a professional FastAPI REST API implementation with:

✅ **JWT Authentication** - Secure token-based authentication  
✅ **Email Verification** - Confirm user emails before access  
✅ **Password Reset** - Secure password recovery flow  
✅ **BREAD Operations** - Browse, Read, Edit, Add, Delete calculations  
✅ **User Statistics** - Track and analyze user activity  
✅ **Modular Architecture** - Clean separation of concerns  
✅ **API Documentation** - Automatic Swagger/ReDoc docs  

## 🚀 Quick Start

### 1. Set Up Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (especially SMTP for email)
```

### 2. Configure Email (Optional)

For email verification to work, configure SMTP settings in `.env`:

```bash
# Gmail Example (use App Password, not regular password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com
```

**How to get Gmail App Password:**
1. Enable 2-Factor Authentication
2. Visit: https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"
4. Use this password in `.env`

### 3. Start the API

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the dev script
./scripts/dev.sh
```

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📚 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | ❌ |
| GET | `/api/auth/verify-email` | Verify email with token | ❌ |
| POST | `/api/auth/resend-verification` | Resend verification email | ❌ |
| POST | `/api/auth/login` | Login and get tokens | ❌ |
| POST | `/api/auth/refresh` | Refresh access token | ❌ |
| POST | `/api/auth/logout` | Logout user | ✅ |
| POST | `/api/auth/forgot-password` | Request password reset | ❌ |
| POST | `/api/auth/reset-password` | Reset password with token | ❌ |
| GET | `/api/auth/me` | Get current user info | ✅ |

### Calculation Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/calculations` | Create calculation | ✅ |
| GET | `/api/calculations` | List all calculations | ✅ |
| GET | `/api/calculations/{id}` | Get specific calculation | ✅ |
| PUT | `/api/calculations/{id}` | Update calculation | ✅ |
| DELETE | `/api/calculations/{id}` | Delete calculation | ✅ |
| GET | `/api/calculations/stats/summary` | Get user statistics | ✅ |

## 🔐 Authentication Flow

### 1. Register New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response:**
```json
{
  "id": "uuid-here",
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_verified": false,
  "is_active": true
}
```

### 2. Verify Email

Check your email for verification link:
```
http://localhost:8000/api/auth/verify-email?token=YOUR_TOKEN
```

Click the link or use curl:
```bash
curl http://localhost:8000/api/auth/verify-email?token=YOUR_TOKEN
```

**Response:**
```json
{
  "message": "Email verified successfully! You can now log in.",
  "email": "john@example.com",
  "is_verified": true
}
```

### 3. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=securepass123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_at": "2025-12-15T10:30:00Z",
  "user": {
    "id": "uuid",
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

### 4. Use Access Token

Include the access token in the Authorization header:

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 Using the API

### Create a Calculation

```bash
curl -X POST http://localhost:8000/api/calculations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "add",
    "operand1": 10.5,
    "operand2": 5.25
  }'
```

**Response:**
```json
{
  "id": "calc-uuid",
  "user_id": "user-uuid",
  "operation": "add",
  "operand1": 10.5,
  "operand2": 5.25,
  "result": 15.75,
  "created_at": "2025-12-15T10:00:00Z",
  "updated_at": "2025-12-15T10:00:00Z"
}
```

### List All Calculations

```bash
curl -X GET http://localhost:8000/api/calculations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get User Statistics

```bash
curl -X GET http://localhost:8000/api/calculations/stats/summary \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "total_calculations": 42,
  "operations": {
    "add": 15,
    "subtract": 10,
    "multiply": 12,
    "divide": 5
  },
  "user": {
    "id": "user-uuid",
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

## 🔒 Security Features

### Password Hashing
- Bcrypt with 12 rounds
- Secure password storage
- No plain text passwords

### JWT Tokens
- Access tokens (30 min expiry)
- Refresh tokens (7 days expiry)
- HS256 algorithm
- Token blacklisting support (Redis)

### Email Verification
- Required before login
- 24-hour token expiration
- Secure token generation
- Resend verification option

### Password Reset
- Secure token-based reset
- 1-hour token expiration
- Email notification
- No user enumeration

## 🧪 Testing

### Run All Tests

```bash
./scripts/test.sh
```

### Test Specific Module

```bash
pytest tests/integration/test_user_auth.py -v
```

### Test with Coverage

```bash
pytest --cov=app --cov-report=html
```

## 📁 Project Structure

```
app/
├── api/                    # API routes (modular)
│   ├── __init__.py
│   ├── auth.py            # Authentication endpoints
│   └── calculations.py    # Calculation endpoints
├── auth/                  # Authentication modules
│   ├── dependencies.py    # Auth dependencies
│   ├── email.py           # Email service
│   ├── jwt.py             # JWT utilities
│   └── redis.py           # Token blacklisting
├── core/                  # Core configuration
│   └── config.py          # Settings
├── models/                # Database models
│   ├── user.py            # User model
│   └── calculation.py     # Calculation model
├── schemas/               # Pydantic schemas
│   ├── user.py            # User schemas
│   ├── calculation.py     # Calculation schemas
│   └── token.py           # Token schemas
└── main.py                # FastAPI application
```

## 🐳 Docker Deployment

### Development

```bash
docker-compose up -d
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `JWT_SECRET_KEY` | JWT signing key | **Required** |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP username | **Required** |
| `SMTP_PASSWORD` | SMTP password | **Required** |
| `BASE_URL` | Application base URL | `http://localhost:8000` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` |
| `EMAIL_VERIFICATION_EXPIRE_HOURS` | Verification expiry | `24` |

## 📖 Additional Documentation

- [Development Guide](DEVELOPMENT.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Operations Guide](OPERATIONS.md)
- [API Documentation](http://localhost:8000/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

See [LICENSE](LICENSE) file for details.

---

**Need Help?** Check the [API Documentation](http://localhost:8000/docs) or raise an issue!
