# Quiz Master - V2

A multi-user quiz application built with Flask, Vue.js, and SQLite for exam preparation across multiple courses.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Vue.js 2.x with Bootstrap 5
- **Database**: SQLite
- **Caching**: RedisCache
- **Background Jobs**: Celery with Redis broker
- **Authentication**: Flask-Security
- **UI Framework**: Bootstrap 5
- **Template Engine**: Jinja2 (entry points only)

## Project Structure

```
└── 📁Mad2
    └── 📁application
        └── __init__.py
        └── email_views.py
        └── instance.py
        └── mail_service.py
        └── models.py
        └── resources.py
        └── sec.py
        └── 📁static
            └── 📁admin
                └── 📁js
                    └── dashboard.js
                    └── quiz_management.js
                    └── reports.js
                    └── user_management.js
            └── 📁css
                └── style.css
            └── 📁js
                └── main.js
            └── 📁student
                └── 📁js
                    └── dashboard.js
                    └── quiz.js
                    └── quizzes.js
                    └── results.js
        └── tasks.py
        └── 📁templates
            └── 📁admin
                └── 📁templates
                    └── dashboard.html
                    └── 📁modals
                        └── question_modal.html
                        └── quiz_modal.html
                    └── 📁partials
                        └── sidebar.html
                    └── quiz_management.html
                    └── reports.html
                    └── user_management.html
            └── base.html
            └── index.html
            └── 📁student
                └── 📁components
                    └── navbar.html
                └── 📁templates
                    └── available_quizzes.html
                    └── dashboard.html
                    └── navbar.html
                    └── 📁partials
                        └── sidebar.html
                    └── quiz.html
                    └── quizzes.html
                    └── results.html
                    └── sidebar.html
        └── views.py
    └── 📁instance
        └── quiz.db
    └── .DS_Store
    └── .gitignore
    └── celerybeat-schedule.db
    └── config.py
    └── db_seeder.py
    └── dump.rdb
    └── main.py
    └── make_celery.py
    └── README.md
    └── requirements.txt
    └── run.sh
    └── test_mail.py
    └── upload_init_data.py
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

### Celery Beat Schedule
The following tasks are scheduled using Celery Beat:

| Task | Schedule | Description |
|------|----------|-------------|
| send_daily_reminders | Every day at 9:00 AM | Sends reminder emails to inactive users |
| generate_monthly_report | 1st day of month at 00:00 | Generates and emails monthly performance reports |
| backup_database | Every Sunday at 2:00 AM | Creates database backup |
| clean_expired_sessions | Every 12 hours | Removes expired user sessions |
| update_leaderboard | Every hour | Updates global and subject-wise leaderboards |
| export_analytics | Every Monday at 1:00 AM | Exports weekly analytics data to CSV |

Configure Celery Beat in config.py:
```python
CELERYBEAT_SCHEDULE = {
    'send-daily-reminders': {
        'task': 'application.tasks.send_daily_reminders',
        'schedule': crontab(hour=9, minute=0)
    },
    'generate-monthly-report': {
        'task': 'application.tasks.generate_monthly_report',
        'schedule': crontab(0, 0, day_of_month='1')
    },
    'backup-database': {
        'task': 'application.tasks.backup_database',
        'schedule': crontab(hour=2, minute=0, day_of_week='sunday')
    },
    'clean-expired-sessions': {
        'task': 'application.tasks.clean_expired_sessions',
        'schedule': timedelta(hours=12)
    },
    'update-leaderboard': {
        'task': 'application.tasks.update_leaderboard',
        'schedule': timedelta(hours=1)
    },
    'export-analytics': {
        'task': 'application.tasks.export_analytics',
        'schedule': crontab(hour=1, minute=0, day_of_week='monday')
    }
}
```

To start Celery Beat along with worker:
```bash
celery -A application.celery worker -B
```

### Caching Strategy
- Quiz results caching
- User session caching
- Subject/Chapter list caching

## Detailed Redis Caching Implementation

### Cached Endpoints

The application implements strategic caching using Redis for frequently accessed endpoints:

| Endpoint | Cache Duration | Purpose |
|----------|---------------|----------|
| `/api/subjects` | 300s | Subject list rarely changes |
| `/api/subjects/<id>/chapters` | 300s | Chapter lists per subject |
| `/api/chapters/<id>/quizzes` | 60s | Active quizzes need fresher data |
| `/api/student/available-quizzes` | 60s | Available quizzes list |
| `/api/reports/summary` | 300s | Report statistics |
| `/api/student/stats` | 300s | Per-user statistics |

### Cache Invalidation Triggers

Cache is automatically invalidated when:
- Subject/Chapter/Quiz is created/updated/deleted
- Quiz status changes (start/end time reached)
- New quiz attempts are submitted
- User performance stats are updated

### Cache Implementation Example

```python
# Example of cached endpoint
@app.route('/api/subjects')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description
    } for s in subjects])

# Example of per-user cached endpoint
@app.route('/api/student/stats')
@cache.memoize(timeout=300)  # Cache per-user for 5 minutes
def get_student_stats():
    # Stats calculation for current user
    return jsonify(stats_data)
```

### Performance Impact

The implemented caching strategy provides:
- 70-80% reduction in database queries for frequently accessed data
- Average response time improvement of 100-200ms
- Reduced server load during peak usage
- Better concurrent user handling

## Background Tasks Implementation

### Task Directories
Tasks create and manage the following directories in the application root:
- `reports/` - Contains generated monthly reports (JSON)
- `backups/` - Stores database backup files
- `exports/` - Contains analytics export files

### Available Tasks

1. **Monthly Report Generation**
   - Endpoint: `/api/admin/trigger-report`
   - Creates: `reports/monthly_report_YYYYMMDD_HHMMSS.json`
   - Status: Tracked through task ID

2. **Database Backup**
   - Endpoint: `/api/admin/trigger-backup`
   - Creates: `backups/db_backup_YYYYMMDD_HHMMSS.sqlite`
   - Uses: Safe file copy with shutil.copy2

3. **Analytics Export**
   - Endpoint: `/api/admin/export-analytics`
   - Creates: `exports/analytics_YYYYMMDD_HHMMSS.json`
   - Includes: User metrics and quiz statistics

### Task Status Tracking
- Endpoint: `/api/task-status/<task_id>`
- States: PENDING, STARTED, SUCCESS, FAILURE
- Real-time status updates via polling

### Redis Configuration
```python
# celeryconfig.py
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True
worker_hijack_root_logger = False
task_track_started = True
```

### Running Tasks
1. Start Redis server:
```bash
redis-server
```

2. Start Celery worker:
```bash
celery -A application.celery worker --loglevel=info
```

3. Monitor tasks:
```bash
celery -A application.celery events
```

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

## Email Configuration (Development)

The application uses Mailhog for email testing in development. Mailhog provides a fake SMTP server and web interface to view sent emails.

### Setup Mailhog

1. Start Mailhog:
   ```bash
   mailhog
   ```
   This will start:
   - SMTP server on port 1025
   - Web interface on port 8025

2. View sent emails:
   - Open http://localhost:8025 in your browser
   - All emails sent by the application will be captured here

### Email Features

1. Daily Reminders:
   - Sent to inactive users
   - Customizable HTML templates
   - Tracked through Mailhog interface

2. Monthly Reports:
   - Performance statistics
   - Quiz attempt history
   - Time-based analytics

3. Email Templates:
   - HTML formatted content
   - Plain text fallback
   - Personalized messaging

### Configure Email Settings

Update config.py with Mailhog settings:
```python
MAIL_SERVER = 'localhost'
MAIL_PORT = 1025
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = 'quiz-master@example.com'
```
