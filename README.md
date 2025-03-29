# Quiz Master - V2

A multi-user quiz application built with Flask, Vue.js, and SQLite for exam preparation across multiple courses.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Vue.js 2.x with Bootstrap 5
- **Database**: SQLite
- **Caching**: Redis
- **Background Jobs**: Celery with Redis broker
- **Authentication**: Flask-Security
- **UI Framework**: Bootstrap 5
- **Template Engine**: Jinja2 (entry points only)

## Project Structure

```
Mad2/
├── application/
│   ├── static/
│   │   ├── admin/
│   │   │   └── js/
│   │   ├── student/
│   │   │   └── js/
│   │   └── js/
│   ├── templates/
│   │   ├── admin/
│   │   ├── student/
│   │   └── base.html
│   ├── models/
│   ├── views.py
│   ├── tasks.py
│   └── __init__.py
├── instance/
│   └── quiz.db
└── config.py
```

## Core Features

### Authentication
- Role-based access (Admin/Student)
- JWT-based authentication
- Session management

### Admin Features
- Subject CRUD operations
- Chapter management
- Quiz creation and management
- User management
- Analytics dashboard

### Student Features
- Quiz attempts with timer
- Performance tracking
- Score history
- Personal analytics

### Background Jobs
1. **Daily Reminders**
   - Checks user activity
   - Sends notifications via email/SMS
   
2. **Monthly Reports**
   - Generates activity summary
   - Sends HTML/PDF reports
   
3. **CSV Exports**
   - Quiz attempt history
   - Performance analytics

### Caching Strategy
- Quiz results caching
- User session caching
- Subject/Chapter list caching

## API Endpoints

### Authentication
- POST `/api/login`
- POST `/api/logout`

### Admin APIs
- GET/POST `/api/subjects`
- GET/POST `/api/chapters`
- GET/POST `/api/quizzes`
- GET `/api/users`

### Student APIs
- GET `/api/quizzes`
- POST `/api/quiz/<id>/attempt`
- GET `/api/results`

## Database Schema

### Users
- id (PK)
- email
- password_hash
- full_name
- role
- qualification
- dob

### Subjects
- id (PK)
- name
- description

### Chapters
- id (PK)
- subject_id (FK)
- name
- description

### Quizzes
- id (PK)
- chapter_id (FK)
- title
- duration
- date_created

### Questions
- id (PK)
- quiz_id (FK)
- question_text
- options (JSON)
- correct_answer

### Results
- id (PK)
- user_id (FK)
- quiz_id (FK)
- score
- attempt_date

## Setup Instructions

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize database:
   ```bash
   flask db upgrade
   ```

4. Start Redis server:
   ```bash
   redis-server
   ```

5. Run Celery worker:
   ```bash
   celery -A application.celery worker
   ```

6. Run application:
   ```bash
   flask run
   ```

## Environment Variables
```
FLASK_APP=application
FLASK_ENV=development
SECRET_KEY=your-secret-key
REDIS_URL=redis://localhost:6379
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-password
```
# Quiz_mater_v2
