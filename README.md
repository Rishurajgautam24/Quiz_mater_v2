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

## Detailed Redis Caching Implementation

### Cache Configuration
- **Engine**: Redis
- **Host**: localhost
- **Port**: 6379
- **Database**: 0
- **Key Prefix**: quiz_app_
- **Default Timeout**: 300 seconds (5 minutes)

### Cache Timeout Levels
- **Short-lived (60s)**: Time-sensitive data (active quizzes, available quizzes)
- **Medium-lived (300s)**: Semi-dynamic data (subject/chapter lists, user stats)
- **Long-lived (3600s)**: Static reference data (system constants, configurations)

### Cached Resources & Invalidation Strategy

| Resource | Cache Duration | Cache Key Pattern | Invalidation Trigger |
|----------|----------------|-------------------|----------------------|
| Subject List | 300s | subject_list_all | Subject Create/Update/Delete |
| Chapter List | 300s | chapter_list_subject_{id} | Chapter Create/Update/Delete |
| Quiz List | 60s | quiz_list_chapter_{id} | Quiz Create/Update/Delete |
| Question List | 300s | questions_quiz_{id} | Question Create/Update/Delete |
| Available Quizzes | 60s | available_quizzes | Quiz Status Changes |
| Student Stats | 300s | student_stats_user_{id} | New Quiz Attempt |
| Reports | 300s | report_summary_{parameters} | New Quiz Attempts |

### Cache Implementation Techniques
1. **Decorator-based Caching**: Using `@cache.cached()` for route-level caching
2. **Memoization**: Using `@cache.memoize()` for function-level caching with parameters
3. **Manual Invalidation**: Strategic cache clearing on data modifications
4. **Selective Caching**: Caching expensive computations and database queries only

### Caching Performance Benefits
- Reduced database load for frequently accessed data
- Lower response times for complex calculations (reports, statistics)
- Better application scalability under concurrent user load
- Consistent performance during peak usage periods

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
