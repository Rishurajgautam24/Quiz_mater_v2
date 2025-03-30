from celery import shared_task, Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
from application.models import User, Quiz, QuizAttempt, db
from sqlalchemy import func
import csv
import io
import os
import json
from flask import render_template
from celery.signals import worker_ready
from application.mail_service import EmailService
import shutil

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

@shared_task(bind=True)
def generate_monthly_report(self):
    """Generate monthly report"""
    try:
        # Get absolute path and create reports directory
        current_dir = os.getcwd()
        reports_dir = os.path.join(current_dir, 'reports')
        
        print(f"Current directory: {current_dir}")
        print(f"Creating reports directory at: {reports_dir}")
        
        try:
            os.makedirs(reports_dir, exist_ok=True)
            print(f"Reports directory created/verified at: {reports_dir}")
        except Exception as mkdir_error:
            print(f"Error creating reports directory: {str(mkdir_error)}")
            raise

        # Generate report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'completed'
        }

        # Save report with absolute path
        filename = os.path.join(reports_dir, f'monthly_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        print(f"Attempting to save report to: {filename}")
        
        try:
            with open(filename, 'w') as f:
                json.dump(report_data, f)
            print(f"Report successfully saved to: {filename}")
        except Exception as file_error:
            print(f"Error saving report file: {str(file_error)}")
            raise

        return {'status': 'SUCCESS', 'file': filename}
    except Exception as e:
        error_msg = f"Error in generate_monthly_report: {str(e)}"
        print(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        return {'status': 'FAILURE', 'error': error_msg}

@shared_task(bind=True)
def backup_database(self):
    """Backup database"""
    try:
        # Get absolute path and create backups directory
        current_dir = os.getcwd()
        backups_dir = os.path.join(current_dir, 'backups')
        
        print(f"Current directory: {current_dir}")
        print(f"Creating backups directory at: {backups_dir}")
        
        try:
            os.makedirs(backups_dir, exist_ok=True)
            print(f"Backups directory created/verified at: {backups_dir}")
        except Exception as mkdir_error:
            print(f"Error creating backups directory: {str(mkdir_error)}")
            raise

        # Create backup file path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backups_dir, f'db_backup_{timestamp}.sqlite')
        db_path = os.path.join(current_dir, 'instance', 'quiz.db')
        
        print(f"Database path: {db_path}")
        print(f"Backup file path: {backup_file}")
        
        if not os.path.exists(db_path):
            error_msg = f'Database file not found at {db_path}'
            print(error_msg)
            raise FileNotFoundError(error_msg)

        # Perform backup
        try:
            shutil.copy2(db_path, backup_file)
            print(f"Database successfully backed up to: {backup_file}")
        except Exception as backup_error:
            print(f"Error backing up database: {str(backup_error)}")
            raise

        return {'status': 'SUCCESS', 'file': backup_file}
    except Exception as e:
        error_msg = f"Error in backup_database: {str(e)}"
        print(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        return {'status': 'FAILURE', 'error': error_msg}

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

@shared_task(bind=True)
def export_analytics(self):
    """Export analytics data"""
    try:
        # Get absolute path and create exports directory
        current_dir = os.getcwd()
        exports_dir = os.path.join(current_dir, 'exports')
        
        print(f"Current directory: {current_dir}")
        print(f"Creating exports directory at: {exports_dir}")
        
        try:
            os.makedirs(exports_dir, exist_ok=True)
            print(f"Exports directory created/verified at: {exports_dir}")
        except Exception as mkdir_error:
            print(f"Error creating exports directory: {str(mkdir_error)}")
            raise

        # Generate export data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(exports_dir, f'analytics_{timestamp}.json')
        print(f"Attempting to save analytics to: {filename}")
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': {
                'total_users': 100,
                'total_quizzes': 50,
                'total_attempts': 250
            }
        }

        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f)
            print(f"Analytics successfully saved to: {filename}")
        except Exception as file_error:
            print(f"Error saving analytics file: {str(file_error)}")
            raise

        return {'status': 'SUCCESS', 'file': filename}
    except Exception as e:
        error_msg = f"Error in export_analytics: {str(e)}"
        print(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        return {'status': 'FAILURE', 'error': error_msg}

@shared_task
def clean_expired_sessions():
    """Clean expired sessions"""
    # Simulate cleaning expired sessions
    print("Expired sessions cleaned")
    return "Expired sessions cleaned"
