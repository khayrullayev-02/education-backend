# Education Management System - Complete API Documentation

## Overview

Comprehensive REST API for education management with role-based access control, financial management, attendance tracking, and exam management.

## Authentication

### Login
\`\`\`
POST /api/auth/login/
Content-Type: application/json

{
  "username": "teacher@example.com",
  "password": "password123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...},
  "redirect": "/teacher_dashboard"
}
\`\`\`

### Register
\`\`\`
POST /api/auth/register/
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "teacher",
  "organization": "org-uuid",
  "branch": "branch-uuid"
}
\`\`\`

### Token Refresh
\`\`\`
POST /api/auth/token/refresh/
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
\`\`\`

## Finance Module

### Student Payments
\`\`\`
GET /api/finance/student-payments/         # List all payments
POST /api/finance/student-payments/        # Create payment
GET /api/finance/student-payments/pending/ # Get pending payments
POST /api/finance/student-payments/{id}/approve/  # Approve payment
GET /api/finance/student-payments/daily_income/   # Daily income
GET /api/finance/student-payments/debtors/        # Debtors list
\`\`\`

### Financial Reports
\`\`\`
GET /api/finance/reports/                    # List all reports
GET /api/finance/reports/daily_report/       # Daily summary
GET /api/finance/reports/weekly_report/      # Weekly summary
GET /api/finance/reports/monthly_report/     # Monthly summary
\`\`\`

### Teacher Payments & Salaries
\`\`\`
GET /api/finance/teacher-payments/           # List all payments
POST /api/finance/teacher-payments/          # Create payment
GET /api/finance/teacher-payments/pending_payments/  # Pending
POST /api/finance/teacher-payments/{id}/approve/      # Approve
POST /api/finance/teacher-payments/{id}/mark_paid/    # Mark as paid
\`\`\`

### Teacher Wallets
\`\`\`
GET /api/finance/wallets/                    # List wallets
GET /api/finance/wallets/{id}/               # Get wallet
GET /api/finance/wallets/{id}/balance/       # Update balance
\`\`\`

### Payment Discounts
\`\`\`
GET /api/finance/discounts/                  # List discounts
POST /api/finance/discounts/                 # Create discount
\`\`\`

### Income Leads
\`\`\`
GET /api/finance/leads/                      # List leads
GET /api/finance/leads/conversion_stats/     # Conversion stats
GET /api/finance/leads/by_source/            # Stats by source
\`\`\`

## Admin Dashboard

### Student Management
\`\`\`
GET /api/admin/students/                     # List students
POST /api/admin/students/                    # Create student
GET /api/admin/students/{id}/                # Get student
PUT /api/admin/students/{id}/                # Update student
DELETE /api/admin/students/{id}/             # Delete student
GET /api/admin/students/debtors/             # Debtors
POST /api/admin/students/{id}/block_student/          # Block
POST /api/admin/students/{id}/unblock_student/        # Unblock
\`\`\`

### Document Approval
\`\`\`
GET /api/admin/documents/                    # List documents
POST /api/admin/documents/                   # Upload document
GET /api/admin/documents/pending/            # Pending approvals
POST /api/admin/documents/{id}/approve/      # Approve
POST /api/admin/documents/{id}/reject/       # Reject
\`\`\`

### Attendance Management
\`\`\`
GET /api/admin/attendance/daily_attendance/  # Daily stats
GET /api/admin/attendance/student_attendance/ # Student history
GET /api/admin/attendance/teacher_lateness/   # Teacher lateness
\`\`\`

## Attendance Module

### Submit Attendance
\`\`\`
POST /api/attendance/submit/submit_attendance/
{
  "lesson_id": "uuid",
  "students_attendance": [
    {
      "student_id": "uuid",
      "status": "present",
      "homework_status": "done",
      "homework_grade": 8,
      "comments": ""
    }
  ],
  "teacher_status": "present"
}
\`\`\`

### View Attendance
\`\`\`
GET /api/attendance/records/                 # List records
GET /api/attendance/records/pending_submission/  # Pending
\`\`\`

## Exam Module

### Exams
\`\`\`
GET /api/exams/                              # List exams
POST /api/exams/                             # Create exam
GET /api/exams/{id}/                         # Get exam
GET /api/exams/{id}/detailed/                # Detailed with results
\`\`\`

### Exam Results
\`\`\`
GET /api/exams/results/                      # List results
POST /api/exams/results/bulk_import/         # Bulk import
GET /api/exams/results/by_grade/             # Group by grade
GET /api/exams/results/statistics/           # Statistics
\`\`\`

### Grade Ranges
\`\`\`
A - Excellent: 86-100
B - Good:      51-85
C - Poor:      0-50
\`\`\`

## Teacher Dashboard

### Dashboard Overview
\`\`\`
GET /api/teacher/dashboard/overview/         # Overview stats
GET /api/teacher/dashboard/my_groups/        # My groups
GET /api/teacher/dashboard/student_attendance/ # Student attendance
GET /api/teacher/dashboard/wallet_info/      # Wallet info
GET /api/teacher/dashboard/upcoming_lessons/ # Next 10 lessons
\`\`\`

### Homework Management
\`\`\`
GET /api/teacher/homework/                   # List homework
POST /api/teacher/homework/                  # Create homework
GET /api/teacher/submissions/                # List submissions
POST /api/teacher/submissions/{id}/grade/    # Grade submission
\`\`\`

## Director Dashboard

### Dashboard Overview
\`\`\`
GET /api/director/dashboard/overview/        # Overview stats
GET /api/director/dashboard/financial_overview/  # Finance summary
GET /api/director/dashboard/teacher_performance/ # Teacher performance
GET /api/director/dashboard/group_statistics/    # Group statistics
GET /api/director/dashboard/student_drop_rate/   # At-risk students
GET /api/director/dashboard/monthly_trends/      # Trends
\`\`\`

## Manager Dashboard

### Dashboard Overview
\`\`\`
GET /api/manager/dashboard/overview/         # Overview stats
GET /api/manager/dashboard/attendance_overview/ # Attendance
GET /api/manager/dashboard/teacher_performance/ # Teacher metrics
GET /api/manager/dashboard/student_progress/    # Student progress
GET /api/manager/dashboard/financial_summary/   # Finance summary
GET /api/manager/dashboard/alerts/              # Alerts
\`\`\`

### Student Transfer
\`\`\`
POST /api/manager/dashboard/transfer_student/
{
  "student_id": "uuid",
  "from_group_id": "uuid",
  "to_group_id": "uuid",
  "reason": "Better level fit"
}
\`\`\`

### Teacher Reassignment
\`\`\`
POST /api/manager/dashboard/reassign_teacher/
{
  "group_id": "uuid",
  "old_teacher_id": "uuid",
  "new_teacher_id": "uuid",
  "reason": "Performance improvement"
}
\`\`\`

## Statistics Module

### Overall Statistics
\`\`\`
GET /api/statistics/student_statistics/      # Student stats
GET /api/statistics/teacher_statistics/      # Teacher stats
GET /api/statistics/attendance_statistics/   # Attendance stats
GET /api/statistics/financial_statistics/    # Finance stats
GET /api/statistics/exam_statistics/         # Exam stats
GET /api/statistics/group_statistics/        # Group stats
\`\`\`

## Error Responses

### 400 Bad Request
\`\`\`json
{
  "error": "Invalid parameters or missing required fields"
}
\`\`\`

### 401 Unauthorized
\`\`\`json
{
  "detail": "Authentication credentials were not provided."
}
\`\`\`

### 403 Forbidden
\`\`\`json
{
  "error": "Permission denied"
}
\`\`\`

### 404 Not Found
\`\`\`json
{
  "error": "Resource not found"
}
\`\`\`

### 500 Server Error
\`\`\`json
{
  "error": "Internal server error"
}
\`\`\`

## Pagination

All list endpoints support pagination:
\`\`\`
GET /api/resource/?page=1&page_size=20
\`\`\`

## Filtering & Search

Search endpoints:
\`\`\`
GET /api/resource/?search=query
\`\`\`

Ordering:
\`\`\`
GET /api/resource/?ordering=-created_at
\`\`\`

## Rate Limiting

- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated users

## Access Control by Role

| Endpoint | Superadmin | Director | Manager | Admin | Teacher | Student |
|----------|-----------|----------|---------|-------|---------|---------|
| Finance Reports | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Student Management | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| Attendance | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Exams | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Teacher Dashboard | N/A | N/A | N/A | N/A | ✓ | ✗ |
| Student Dashboard | N/A | N/A | N/A | N/A | N/A | ✓ |

## Support

For issues and questions:
- Email: api@education.uz
- Documentation: /swagger/
- ReDoc: /redoc/
