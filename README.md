# Secure File-Sharing System

![Build](https://github.com/yourusername/secure-file-sharing/actions/workflows/ci-cd.yml/badge.svg)

A secure REST API-based file-sharing system built with FastAPI that supports role-based access control and secure file downloads using encrypted URLs.

## Features

- **Authentication System**
  - JWT-based authentication for two user roles (Operations and Client)
  - Role-based access control
  - Email verification for Client users
  - Secure password hashing

- **File Management**
  - Restricted file uploads (.pptx, .docx, .xlsx) for Operations users
  - File listing for Client users
  - Secure, encrypted download links

- **Security Features**
  - File type validation
  - File size limits
  - Rate limiting
  - Token expiration
  - Error handling

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **Authentication**: JWT tokens
- **Email**: SMTP for verification emails
- **Encryption**: Fernet (for download links)
- **Testing**: Pytest
- **Deployment**: Docker & Docker Compose

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (optional, SQLite works for testing)
- SMTP server access (for email verification)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/secure-file-sharing.git
   cd secure-file-sharing
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   ```bash
   # Create .env file with the following variables
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DATABASE_URL=sqlite:///./sql_app.db  # Use SQLite for development
   SMTP_HOST=smtp.example.com
   SMTP_PORT=587
   SMTP_USER=your_email@example.com
   SMTP_PASSWORD=your_password
   EMAIL_FROM=your_email@example.com
   BASE_URL=http://localhost:8000
   MAX_UPLOAD_SIZE=5242880  # 5MB in bytes
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API documentation**
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Docker Setup

1. **Build and run using Docker Compose**
   ```bash
   docker-compose up -d
   ```

## API Endpoints

### Authentication

- `POST /auth/signup` - Register a new Client user
- `GET /auth/verify-email` - Verify email with token
- `POST /auth/login` - Login for both user types

### File Operations

- `POST /api/upload` - Upload files (Operations users only)
- `GET /api/files` - List all files (Client users only)
- `GET /api/download-file/{file_id}` - Get secure download link (Client users only)
- `GET /download/{token}` - Download file using secure token (Client users only)

## Testing

### Running Tests

```bash
pytest
```

### Manual Testing with Postman

1. Import the included Postman collection
2. Set up environment variables in Postman:
   - `base_url` - Your API base URL (e.g., http://localhost:8000)
   - The collection will automatically store tokens when you login

3. Testing flow:
   - First run the Operations user login request
   - Then upload files as Operations user
   - Switch to Client user login
   - List files and generate download links

## Deployment

The project includes Docker configuration and a GitHub Actions CI/CD workflow for automated testing and deployment:

1. Tests run automatically on push to main branch
2. If tests pass, a Docker image is built and pushed
3. The application is deployed to the configured server

### Production Considerations

- Use a proper database (PostgreSQL recommended)
- Set up proper SSL/TLS for the API
- Configure proper email service for production
- Implement logging and monitoring
- Consider scaling options for file storage

## License

[MIT License](LICENSE)
