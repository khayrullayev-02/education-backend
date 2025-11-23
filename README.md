# Education Management System - Complete Backend

Komprehensiv o'quv markazlari uchun Django REST Framework bilan qurilgan complete backend tizimidir.

## Loyiha Tavsifi

Bu sistema o'quvchilar, o'qituvchilar, adminlar, menejerlar va direktiorlar uchun to'liq o'quv jarayonini boshqarish imkoniyatini beradi. Moliya bo'limi, davomatni nazorat qilish, imtihonlar, ish jadvallari va boshqa ko'plab funktsiyalar mavjud.

### Asosiy Xususiyatlar

- **Role-Based Access Control** - 6 ta turli foydalanuvchi roli
- **Finance Management** - Pul oqimi, oylik hisoblash, daromad tahlili
- **Attendance Tracking** - Avtomatik davomatni qo'yish va tahlili
- **Exam Management** - Test yaratish, natijalari kiritish, grading
- **Homework System** - Uy vazifalarini taqdim etish, bahola berish
- **Real-time Alerts** - O'qituvchi kech qolsa, o'quvchi kelmasa xabar
- **Comprehensive Reports** - Kunlik, haftalik, oylik hisobotlar
- **Multi-branch Support** - Bir nechta filiallarni boshqarish

## Texnologiyalar

- **Backend**: Python 3.9+ + Django 4.2
- **API Framework**: Django REST Framework
- **Database**: PostgreSQL 12+
- **Authentication**: JWT (SimpleJWT)
- **API Documentation**: Swagger/OpenAPI
- **Server**: Gunicorn/uWSGI
- **Cache**: Redis (optional)

## O'rnatish

### 1. Repository klonlash
\`\`\`bash
git clone <repo-url>
cd education-management-backend
\`\`\`

### 2. Virtual Environment yaratish
\`\`\`bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
\`\`\`

### 3. Dependensiyalarni o'rnatish
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Environment variables (.env)
\`\`\`
SECRET_KEY=your-secret-key-change-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=education_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256

# Cors
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
\`\`\`

### 5. Database Setup
\`\`\`bash
python manage.py migrate
\`\`\`

### 6. Superadmin yaratish
\`\`\`bash
python manage.py createsuperuser
\`\`\`

### 7. Server ishga tushirish
\`\`\`bash
python manage.py runserver
\`\`\`

**API**: http://localhost:8000/api/
**Admin**: http://localhost:8000/admin/
**Swagger**: http://localhost:8000/swagger/
**ReDoc**: http://localhost:8000/redoc/

## JWT Autentifikatsiya

### Login
\`\`\`bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "password123"
  }'
\`\`\`

### Response
\`\`\`json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "username": "user@example.com",
    "role": "teacher",
    "redirect": "/teacher_dashboard"
  }
}
\`\`\`

### API Request
\`\`\`bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
\`\`\`

## Foydalanuvchi Rollari

### 1. Superadmin
- Barcha markazlarni boshqarish
- Tariff tizimini sozlash
- Backup yaratish
- System logs ko'rish

### 2. Director
- Filial boshqaruvi
- Moliya monitoring
- Teacher performance baholash
- Student drop rate analizi

### 3. Manager
- Guruhlarni boshqarish
- Teacher reassignment
- Student transfer
- Attendance nazorati

### 4. Admin
- Student CRUD
- To'lov qabul qilish
- Dokumentlarni tasdiqlash
- Davomatni tasdiklash

### 5. Teacher
- O'z guruhlarida davam qo'yish
- Uy vazifasini berish
- Imtihon natijalari kiritish
- Student progress ko'rish

### 6. Student
- Uy vazifalarini ko'rish va taqdim etish
- Imtihon natijalari ko'rish
- To'lov tarixi ko'rish
- Attendance ko'rish

## API Endpoints

### Authentication
\`\`\`
POST   /api/auth/login/              - Login
POST   /api/auth/register/           - Register
GET    /api/auth/profile/            - Get profile
PUT    /api/auth/profile/            - Update profile
POST   /api/auth/change-password/    - Change password
POST   /api/auth/token/refresh/      - Refresh token
\`\`\`

### Finance (Director/Admin)
\`\`\`
GET    /api/finance/reports/                        - Finance reports
GET    /api/finance/reports/daily_report/           - Daily summary
GET    /api/finance/student-payments/               - Student payments
POST   /api/finance/student-payments/{id}/approve/  - Approve payment
GET    /api/finance/teacher-payments/               - Teacher payments
POST   /api/finance/teacher-payments/{id}/mark_paid/ - Mark paid
GET    /api/finance/wallets/                        - Teacher wallets
\`\`\`

### Admin Dashboard
\`\`\`
GET    /api/admin/students/                  - List students
POST   /api/admin/students/                  - Create student
GET    /api/admin/documents/pending/         - Pending documents
POST   /api/admin/documents/{id}/approve/    - Approve document
GET    /api/admin/attendance/daily_attendance/ - Daily attendance
\`\`\`

### Teacher Dashboard
\`\`\`
GET    /api/teacher/dashboard/overview/           - Overview
GET    /api/teacher/dashboard/my_groups/          - My groups
GET    /api/teacher/homework/                     - Homework list
POST   /api/teacher/homework/                     - Create homework
GET    /api/teacher/submissions/                  - Submissions
POST   /api/teacher/submissions/{id}/grade/       - Grade submission
\`\`\`

### Attendance
\`\`\`
POST   /api/attendance/submit/submit_attendance/        - Submit attendance
GET    /api/attendance/records/                         - Attendance records
GET    /api/attendance/submit/select_all_present/       - Select all present
GET    /api/attendance/records/pending_submission/      - Pending
\`\`\`

### Exams
\`\`\`
GET    /api/exams/                           - List exams
POST   /api/exams/                           - Create exam
GET    /api/exams/results/                   - Exam results
POST   /api/exams/results/bulk_import/       - Bulk import results
GET    /api/exams/results/statistics/        - Result statistics
\`\`\`

### Statistics
\`\`\`
GET    /api/statistics/student_statistics/     - Student stats
GET    /api/statistics/teacher_statistics/     - Teacher stats
GET    /api/statistics/attendance_statistics/  - Attendance stats
GET    /api/statistics/financial_statistics/   - Finance stats
GET    /api/statistics/exam_statistics/        - Exam stats
\`\`\`

## Database Schema

### Core Tables
- **CustomUser** - Authentication & users
- **Organization** - Education centers
- **Branch** - Filials
- **Student** - Students
- **Teacher** - Teachers
- **Group** - Study groups
- **Lesson** - Lessons/classes

### Attendance & Exams
- **Attendance** - Attendance records
- **Exam** - Exams
- **ExamResult** - Exam results

### Finance
- **StudentPayment** - Student payments
- **TeacherPayment** - Teacher salaries
- **Wallet** - Teacher wallets
- **FinanceReport** - Daily/weekly/monthly reports

### Other
- **Homework** - Homework assignments
- **HomeworkSubmission** - Student submissions
- **Notification** - System notifications
- **SystemLog** - Activity logs

## Moliya Bo'limi

### Pul Oqimi
\`\`\`
Kirimlar:
  - Student to'lovlari → StudentPayment
  - To'lov summasi avtomatik student.total_paid ga qo'shiladi

Chiqimlar:
  - Teacher oylik → TeacherPayment
  - Staff oylik → StaffPayment
  - Boshqa xarajatlar → FinanceReport.other_expenses

Daromad:
  - Profit = Jami kirimlar - Jami chiqimlar
  - Har kuni avtomatik hisoblanadi
\`\`\`

### Reportlar
- **Daily** - Kunlik kirim-chiqim
- **Weekly** - Haftalik to'plam
- **Monthly** - Oylik analiz

## Deployment

### Docker
\`\`\`bash
docker build -t education-api .
docker run -p 8000:8000 education-api
\`\`\`

### Gunicorn
\`\`\`bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
\`\`\`

### Nginx
\`\`\`nginx
server {
    listen 80;
    server_name api.education.uz;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
\`\`\`

## Testing

\`\`\`bash
python manage.py test
python manage.py test core
python manage.py test finance
python manage.py test attendance
\`\`\`

## Logging

Barcha API requests va errors `/var/log/education/` da saqlanadi.

## Performance

- Querylar optimized (select_related, prefetch_related)
- Pagination: default 20 items per page
- Caching: Redis (optional)
- Rate limiting: 1000 requests/hour

## Security

- JWT Token-based authentication
- CORS enabled (configured origins)
- SQL Injection protection (Django ORM)
- XSS protection (DRF)
- CSRF protection
- Rate limiting
- Input validation

## Support & Contributing

Issues va savollari uchun:
- Email: api@education.uz
- GitHub: github.com/education/backend
- Documentation: /swagger/ yoki /redoc/

## License

MIT License

## Changelog

### v1.0.0
- Complete backend system with all dashboards
- Finance module with wallet system
- Attendance tracking and reporting
- Exam management with grading
- Role-based access control
- Comprehensive API documentation
