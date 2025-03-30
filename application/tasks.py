from celery import shared_task, Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
from application.models import User, Quiz, QuizAttempt, db
from sqlalchemy import func
import csv
import io
from flask import render_template
from celery.signals import worker_ready
from application.mail_service import EmailService

app = Celery()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Daily reminders at 9:00 AM
    sender.add_periodic_task(
        crontab(hour=9, minute=0),
        send_daily_reminders.s(),
        name='daily-reminders'
    )
    
    # Monthly reports on 1st day of month
    sender.add_periodic_task(
        crontab(0, 0, day_of_month='1'),
        generate_monthly_report.s(),
        name='monthly-report'
    )
    
    # Database backup every Sunday at 2 AM
    sender.add_periodic_task(
        crontab(hour=2, minute=0, day_of_week='sunday'),
        backup_database.s(),
        name='weekly-backup'
    )
    
    # Clean expired sessions every 12 hours
    sender.add_periodic_task(
        timedelta(hours=12),
        clean_expired_sessions.s(),
        name='clean-sessions'
    )
    
    # Update leaderboard every hour
    sender.add_periodic_task(
        timedelta(hours=1),
        update_leaderboard.s(),
        name='update-leaderboard'
    )
    
    # Export analytics every Monday at 1 AM
    sender.add_periodic_task(
        crontab(hour=18, minute=43, day_of_week='sunday'),
        export_analytics.s(),
        name='export-analytics'
    )

@shared_task
def send_daily_reminders():
    """Send reminders to inactive users daily"""
    cutoff_date = datetime.now() - timedelta(days=7)
    inactive_users = User.query.join(QuizAttempt).filter(
        QuizAttempt.date_created < cutoff_date
    ).all()
    
    for user in inactive_users:
        EmailService.send_reminder(user.email, user.username)
    return f"Sent reminders to {len(inactive_users)} users"

@shared_task
def generate_monthly_report():
    """Generate monthly performance reports"""
    now = datetime.now()
    start_date = now - timedelta(days=30)
    
    users = User.query.all()
    for user in users:
        attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.date_created >= start_date
        ).all()
        
        if attempts:
            report_data = {
                'total_quizzes': len(attempts),
                'avg_score': sum(a.score for a in attempts) / len(attempts),
                'total_time': sum(a.duration for a in attempts if a.duration)
            }
            EmailService.send_report(user.email, user.username, report_data)
            
    return "Monthly reports generated and sent"

@shared_task
def backup_database():
    """Create database backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Simulate database backup
    print(f"Database backed up: quiz_backup_{timestamp}.sql")
    return f"Backup completed: quiz_backup_{timestamp}.sql"

@shared_task
def update_leaderboard():
    """Update global and subject-wise leaderboards"""
    # Calculate global rankings
    global_leaders = db.session.query(
        User.id,
        User.username,
        func.avg(QuizAttempt.score).label('avg_score')
    ).join(QuizAttempt).group_by(User.id).order_by(
        func.avg(QuizAttempt.score).desc()
    ).limit(10).all()
    
    # Store in cache or database
    return "Leaderboard updated"

@shared_task
def export_analytics():
    """Export weekly analytics data to CSV"""
    start_date = datetime.now() - timedelta(days=7)
    
    attempts = QuizAttempt.query.filter(
        QuizAttempt.date_created >= start_date
    ).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['User', 'Quiz', 'Score', 'Date'])
    
    for attempt in attempts:
        writer.writerow([
            attempt.user.username,
            attempt.quiz.title,
            attempt.score,
            attempt.date_created
        ])
    
    # Simulate file saving
    print(f"Analytics exported: analytics_{start_date.strftime('%Y%m%d')}.csv")
    return "Analytics exported successfully"

@shared_task
def clean_expired_sessions():
    """Clean expired sessions"""
    # Simulate cleaning expired sessions
    print("Expired sessions cleaned")
    return "Expired sessions cleaned"
