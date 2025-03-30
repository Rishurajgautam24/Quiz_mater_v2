# ------------- Imports -------------
from flask import render_template, redirect, url_for, jsonify, request
from flask_security import current_user, roles_required
from flask import current_app as app
from application.models import Subject, Chapter, Quiz, Question, QuizAttempt, db
from application.models import User, Role
from uuid import uuid4
from sqlalchemy import case, func
from datetime import datetime, timedelta
from application.tasks import generate_monthly_report, backup_database, export_analytics
from .instance import cache
import os

# ------------- Admin Dashboard Routes -------------
@app.route('/admin/dashboard')
@roles_required('admin')
def admin_dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('admin/templates/dashboard.html')

@app.route('/admin/quiz-management')
@roles_required('admin')
def quiz_management():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('admin/templates/quiz_management.html')

@app.route('/admin/user-management')
@roles_required('admin')
def user_management():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('admin/templates/user_management.html')

@app.route('/admin/reports')
@roles_required('admin')
def reports():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('admin/templates/reports.html')

@app.route('/admin/tasks')
@roles_required('admin')
def admin_tasks():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('admin/templates/tasks.html')

# ------------- Student Dashboard Routes -------------
@app.route('/student/dashboard')
@roles_required('stud')
def student_dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('student/templates/dashboard.html')

@app.route('/student/quizzes')
@roles_required('stud')
def student_quizzes():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('student/templates/quizzes.html')

@app.route('/student/results')
@roles_required('stud')
def student_results():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('student/templates/results.html')

@app.route('/api/current-user')
def get_current_user():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({
        'username': current_user.username,
        'email': current_user.email
    })

# ------------- Subject API Routes -------------
@app.route('/api/subjects', methods=['GET'])
@cache.cached(timeout=300)  # Cache subject list for 5 minutes
def get_subjects():
    """Get All Subjects With Their Chapter Counts"""
    subjects = Subject.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'chapters_count': len(s.chapters)
    } for s in subjects])

@app.route('/api/subjects', methods=['POST'])
@roles_required('admin')
def create_subject():
    data = request.get_json()
    subject = Subject(name=data['name'], description=data.get('description', ''))
    db.session.add(subject)
    db.session.commit()
    return jsonify({'id': subject.id, 'name': subject.name}), 201

@app.route('/api/subjects/<int:id>', methods=['PUT'])
@roles_required('admin')
def update_subject(id):
    """Update Existing Subject Details"""
    try:
        subject = Subject.query.get_or_404(id)
        data = request.get_json()
        
        if 'name' in data:
            subject.name = data['name']
        if 'description' in data:
            subject.description = data['description']
            
        db.session.commit()
        return jsonify({
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'chapters_count': len(subject.chapters)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/subjects/<int:id>', methods=['DELETE'])
@roles_required('admin')
def delete_subject(id):
    try:
        subject = Subject.query.get_or_404(id)
        db.session.delete(subject)
        db.session.commit()
        return jsonify({'message': 'Subject deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ------------- Chapter API Routes -------------
@app.route('/api/subjects/<int:subject_id>/chapters', methods=['GET'])
@cache.cached(timeout=300)  # Cache chapter list for 5 minutes
def get_chapters(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'quizzes_count': len(c.quizzes),
        'subject_id': c.subject_id  # Add subject_id to the response
    } for c in chapters])

@app.route('/api/chapters', methods=['POST'])
@roles_required('admin')
def create_chapter():
    """Create New Chapter Under A Subject"""
    data = request.get_json()
    chapter = Chapter(
        subject_id=data['subject_id'],
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(chapter)
    db.session.commit()
    return jsonify({'id': chapter.id, 'name': chapter.name}), 201

@app.route('/api/chapters/<int:id>', methods=['PUT'])
@roles_required('admin')
def update_chapter(id):
    try:
        chapter = Chapter.query.get_or_404(id)
        data = request.get_json()
        
        if 'name' in data:
            chapter.name = data['name']
        if 'description' in data:
            chapter.description = data['description']
            
        db.session.commit()
        return jsonify({
            'id': chapter.id,
            'name': chapter.name,
            'description': chapter.description,
            'quizzes_count': len(chapter.quizzes)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/chapters/<int:id>', methods=['DELETE'])
@roles_required('admin')
def delete_chapter(id):
    try:
        chapter = Chapter.query.get_or_404(id)
        db.session.delete(chapter)
        db.session.commit()
        return jsonify({'message': 'Chapter deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ------------- Quiz API Routes -------------
@app.route('/api/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@cache.cached(timeout=60)  # Cache quiz list for 1 minute since it changes more frequently
def get_quizzes(chapter_id):
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    current_time = datetime.now()  # Use local system time
    return jsonify([{
        'id': q.id,
        'title': q.title,
        'description': q.description,
        'duration': q.duration,
        'start_time': q.start_time.isoformat() if q.start_time else None,
        'end_time': q.end_time.isoformat() if q.end_time else None,
        'questions_count': len(q.questions),
        'status': 'active' if (q.start_time and q.end_time and 
                             q.start_time <= current_time <= q.end_time) else 'inactive'
    } for q in quizzes])

@app.route('/api/quizzes', methods=['POST'])
@roles_required('admin')
def create_quiz():
    data = request.get_json()
    try:
        if not all(key in data for key in ['title', 'duration', 'chapter_id']):
            return jsonify({'error': 'Missing required fields'}), 400

        # Parse the time directly from the string without timezone handling
        start_time = datetime.now()
        if data.get('start_time'):
            try:
                # Parse the datetime string directly - keeping the exact hours/minutes entered
                date_str = data['start_time']
                # Convert "YYYY-MM-DDTHH:MM" to datetime object
                start_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
            except Exception as e:
                app.logger.error(f"Error parsing start_time: {str(e)}")
                start_time = datetime.now()
                
        # Calculate end time based on duration in minutes
        duration_minutes = int(data['duration'])
        end_time = start_time + timedelta(minutes=duration_minutes)

        quiz = Quiz(
            chapter_id=data['chapter_id'],
            title=data['title'],
            description=data.get('description', ''),
            duration=duration_minutes,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(quiz)
        db.session.commit()
        
        return jsonify({
            'id': quiz.id,
            'title': quiz.title,
            'duration': quiz.duration,
            'start_time': quiz.start_time.isoformat(),
            'end_time': quiz.end_time.isoformat(),
            'status': 'active' if start_time <= datetime.now() <= end_time else 'inactive'
        }), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating quiz: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/quizzes/<int:id>', methods=['PUT'])
@roles_required('admin')
def update_quiz(id):
    try:
        quiz = Quiz.query.get_or_404(id)
        data = request.get_json()
        
        # Update quiz fields
        quiz.title = data.get('title', quiz.title)
        quiz.description = data.get('description', quiz.description)
        
        # Update duration if provided
        if 'duration' in data:
            quiz.duration = data['duration']
        
        # Update timing with direct string parsing
        if data.get('start_time'):
            try:
                # Parse the datetime string directly
                date_str = data['start_time']
                # Convert "YYYY-MM-DDTHH:MM" to datetime object
                start_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
                quiz.start_time = start_time
                # Recalculate end_time based on start_time + duration
                quiz.end_time = start_time + timedelta(minutes=quiz.duration)
            except Exception as e:
                app.logger.error(f"Error parsing start_time for update: {str(e)}")
                return jsonify({'error': f"Invalid start time format: {str(e)}"}), 400
            
        db.session.commit()
        
        # Use current system time for status calculation
        now = datetime.now()
        return jsonify({
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'duration': quiz.duration,
            'start_time': quiz.start_time.isoformat() if quiz.start_time else None,
            'end_time': quiz.end_time.isoformat() if quiz.end_time else None,
            'questions_count': len(quiz.questions),
            'status': 'active' if (quiz.start_time <= now <= quiz.end_time) else 'inactive'
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating quiz: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/quizzes/<int:id>', methods=['DELETE'])
@roles_required('admin')
def delete_quiz(id):
    try:
        # Start a transaction
        quiz = Quiz.query.get_or_404(id)
        
        # Delete all related quiz attempts first
        QuizAttempt.query.filter_by(quiz_id=id).delete()
        
        # Delete all questions
        Question.query.filter_by(quiz_id=id).delete()
        
        # Finally delete the quiz
        db.session.delete(quiz)
        db.session.commit()
        
        return jsonify({'message': 'Quiz deleted successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting quiz {id}: {str(e)}")
        return jsonify({'error': 'Failed to delete quiz'}), 500

# ------------- Question API Routes -------------
@app.route('/api/quizzes/<int:quiz_id>/questions', methods=['GET'])
def get_questions(quiz_id):
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return jsonify([{
        'id': q.id,
        'question_text': q.question_text,
        'options': q.options,
        'correct_answer': q.correct_answer,
        'marks': q.marks
    } for q in questions])

@app.route('/api/questions', methods=['POST'])
@roles_required('admin')
def create_question():
    data = request.get_json()
    question = Question(
        quiz_id=data['quiz_id'],
        question_text=data['question_text'],
        options=data['options'],
        correct_answer=data['correct_answer'],
        marks=data.get('marks', 1)
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({'id': question.id}), 201

@app.route('/api/questions/<int:id>', methods=['PUT', 'DELETE'])
@roles_required('admin')
def manage_question(id):
    question = Question.query.get_or_404(id)
    
    if request.method == 'DELETE':
        db.session.delete(question)
        db.session.commit()
        return jsonify({'message': 'Question deleted successfully'})
        
    data = request.get_json()
    question.question_text = data['question_text']
    question.options = data['options']
    question.correct_answer = data['correct_answer']
    question.marks = data.get('marks', 1)
    
    db.session.commit()
    return jsonify({
        'id': question.id,
        'question_text': question.question_text,
        'options': question.options,
        'correct_answer': question.correct_answer,
        'marks': question.marks
    })

# ------------- User Management API Routes -------------
@app.route('/api/users', methods=['GET'])
@roles_required('admin')
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'active': u.active,
        'roles': [role.name for role in u.roles]
    } for u in users])

@app.route('/api/users', methods=['POST'])
@roles_required('admin')
def create_user():
    data = request.get_json()
    try:
        user = User(
            username=data['username'],
            email=data['email'],
            active=True,
            fs_uniquifier=str(uuid4())
        )
        user.set_password(data['password'])
        
        # Add roles
        for role_name in data.get('roles', []):
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)
        
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/users/<int:id>', methods=['PUT'])
@roles_required('admin')
def update_user(id):
    try:
        user = User.query.get_or_404(id)
        data = request.get_json()
        
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        if 'roles' in data:
            user.roles = []
            for role_name in data['roles']:
                role = Role.query.filter_by(name=role_name).first()
                if role:
                    user.roles.append(role)
        
        db.session.commit()
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'active': user.active,
            'roles': [role.name for role in user.roles]
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/users/<int:id>', methods=['DELETE'])
@roles_required('admin')
def delete_user(id):
    try:
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/users/<int:id>/toggle-status', methods=['PATCH'])
@roles_required('admin')
def toggle_user_status(id):
    try:
        user = User.query.get_or_404(id)
        user.active = not user.active
        db.session.commit()
        return jsonify({
            'id': user.id,
            'active': user.active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ------------- Report Generation API Routes -------------
@app.route('/api/reports/summary')
@roles_required('admin')
@cache.cached(timeout=300)  # Cache report summary for 5 minutes
def report_summary():
    """Get summary statistics for reporting"""
    try:
        time_period = request.args.get('time_period', 'all')
        subject_id = request.args.get('subject_id')
        chapter_id = request.args.get('chapter_id')
        
        # Base query for quiz attempts
        attempts_query = db.session.query(QuizAttempt)
        
        # Apply filters
        if time_period != 'all':
            from datetime import datetime, timedelta
            today = datetime.now()
            if time_period == '7days':
                start_date = today - timedelta(days=7)
            elif time_period == '30days':
                start_date = today - timedelta(days=30)
            elif time_period == '90days':
                start_date = today - timedelta(days=90)
            attempts_query = attempts_query.filter(QuizAttempt.date_created >= start_date)
        
        # Subject and chapter filters require joins
        if subject_id or chapter_id:
            attempts_query = attempts_query.join(Quiz)
            
            if chapter_id:
                attempts_query = attempts_query.filter(Quiz.chapter_id == chapter_id)
            elif subject_id:
                attempts_query = attempts_query.join(Chapter).filter(Chapter.subject_id == subject_id)
        
        # Execute the queries with appropriate filtering
        total_attempts = attempts_query.count()
        
        # If there are no attempts, return zeros to avoid division errors
        if total_attempts == 0:
            return jsonify({
                'totalAttempts': 0,
                'averageScore': 0,
                'activeUsers': 0,
                'totalQuizzes': 0
            })
        
        # Calculate average score - we need to get the sum of all scores first
        from sqlalchemy import func
        avg_score = db.session.query(func.avg(QuizAttempt.score)).scalar() or 0
        avg_score = round(float(avg_score), 1)
        
        # Count distinct users who have taken quizzes
        distinct_users = db.session.query(func.count(func.distinct(QuizAttempt.user_id))).scalar() or 0
        
        # Count total quizzes (respecting filters)
        quizzes_query = db.session.query(Quiz)
        if chapter_id:
            quizzes_query = quizzes_query.filter(Quiz.chapter_id == chapter_id)
        elif subject_id:
            quizzes_query = quizzes_query.join(Chapter).filter(Chapter.subject_id == subject_id)
        total_quizzes = quizzes_query.count()
        
        return jsonify({
            'totalAttempts': total_attempts,
            'averageScore': avg_score,
            'activeUsers': distinct_users,
            'totalQuizzes': total_quizzes
        })
    except Exception as e:
        app.logger.error(f"Error generating summary report: {str(e)}")
        return jsonify({
            'totalAttempts': 0,
            'averageScore': 0,
            'activeUsers': 0,
            'totalQuizzes': 0
        })

@app.route('/api/reports/quiz-activity')
@roles_required('admin')
def report_quiz_activity():
    """Get quiz activity data for reporting"""
    try:
        time_period = request.args.get('time_period', 'all')
        subject_id = request.args.get('subject_id')
        chapter_id = request.args.get('chapter_id')
        
        # Base query - join all necessary tables
        from sqlalchemy import func
        query = db.session.query(
            Quiz.id.label('quiz_id'),
            Quiz.title.label('quiz_title'),
            Chapter.name.label('chapter_name'),
            Subject.name.label('subject_name'),
            func.count(QuizAttempt.id).label('attempts'),
            func.avg(QuizAttempt.score).label('avg_score'),
            # Pass rate calculation (scores >= 40%)
            (func.sum(case((QuizAttempt.score >= 40, 1), else_=0)) / func.count(QuizAttempt.id) * 100).label('pass_rate')
        ).join(Quiz, QuizAttempt.quiz_id == Quiz.id)\
         .join(Chapter, Quiz.chapter_id == Chapter.id)\
         .join(Subject, Chapter.subject_id == Subject.id)
        
        # Apply filters
        if time_period != 'all':
            from datetime import datetime, timedelta
            today = datetime.now()
            if time_period == '7days':
                start_date = today - timedelta(days=7)
            elif time_period == '30days':
                start_date = today - timedelta(days=30)
            elif time_period == '90days':
                start_date = today - timedelta(days=90)
            query = query.filter(QuizAttempt.date_created >= start_date)
        
        if chapter_id:
            query = query.filter(Quiz.chapter_id == chapter_id)
        elif subject_id:
            query = query.filter(Subject.id == subject_id)
        
        # Group by quiz and execute query
        query = query.group_by(Quiz.id, Quiz.title, Chapter.name, Subject.name)
        results = query.all()
        
        # If no data, return empty list
        if not results:
            return jsonify([])
        
        # Format the results
        formatted_results = []
        for row in results:
            formatted_results.append({
                'quiz_id': row.quiz_id,
                'quiz_title': row.quiz_title,
                'chapter_name': row.chapter_name,
                'subject_name': row.subject_name,
                'attempts': row.attempts,
                'avg_score': round(float(row.avg_score or 0), 1),
                'pass_rate': round(float(row.pass_rate or 0), 1)
            })
        
        return jsonify(formatted_results)
    except Exception as e:
        app.logger.error(f"Error generating quiz activity report: {str(e)}")
        return jsonify([])

@app.route('/api/reports/time-series')
@roles_required('admin')
def report_time_series():
    """Get time series data for performance chart"""
    try:
        time_period = request.args.get('time_period', 'all')
        subject_id = request.args.get('subject_id')
        chapter_id = request.args.get('chapter_id')
        
        # Determine date range based on time period
        from datetime import datetime, timedelta
        today = datetime.now().date()
        
        if time_period == '7days':
            days = 7
        elif time_period == '30days':
            days = 30
        elif time_period == '90days':
            days = 90
        else:  # Default to last 7 days if 'all' to avoid too much data
            days = 7
        
        start_date = today - timedelta(days=days-1)
        
        # Generate all dates in the range
        date_range = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
        
        # Base query with date formatting and grouping
        from sqlalchemy import func, cast, Date
        query = db.session.query(
            cast(QuizAttempt.date_created, Date).label('attempt_date'),
            func.avg(QuizAttempt.score).label('avg_score'),
            func.count(QuizAttempt.id).label('attempts')
        )
        
        # Apply filters
        query = query.filter(QuizAttempt.date_created >= start_date)
        
        if chapter_id or subject_id:
            query = query.join(Quiz)
            
            if chapter_id:
                query = query.filter(Quiz.chapter_id == chapter_id)
            elif subject_id:
                query = query.join(Chapter).filter(Chapter.subject_id == subject_id)
        
        # Group by date and execute
        query = query.group_by('attempt_date').order_by('attempt_date')
        results = query.all()
        
        # Create a lookup dictionary for actual data
        data_by_date = {
            row.attempt_date.strftime('%Y-%m-%d'): {
                'avg_score': round(float(row.avg_score), 1) if row.avg_score else 0,
                'attempts': row.attempts
            } for row in results
        }
        
        # Build the final time series with all dates (filling gaps with zeros)
        time_data = []
        for date_str in date_range:
            if date_str in data_by_date:
                time_data.append({
                    'date': date_str,
                    'avg_score': data_by_date[date_str]['avg_score'],
                    'attempts': data_by_date[date_str]['attempts']
                })
            else:
                time_data.append({
                    'date': date_str,
                    'avg_score': 0,
                    'attempts': 0
                })
        
        return jsonify(time_data)
    except Exception as e:
        app.logger.error(f"Error generating time series report: {str(e)}")
        # Return empty data for the requested range
        from datetime import datetime, timedelta
        today = datetime.now().date()
        
        if time_period == '7days':
            days = 7
        elif time_period == '30days':
            days = 30
        elif time_period == '90days':
            days = 90
        else:
            days = 7
            
        start_date = today - timedelta(days=days-1)
        date_range = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
        
        return jsonify([{'date': date_str, 'avg_score': 0, 'attempts': 0} for date_str in date_range])

# ------------ Celery beats configurations -----------
@app.route('/api/admin/trigger-report')
@roles_required('admin')
def trigger_report():
    """Manually trigger monthly report generation"""
    try:
        # Create necessary directories
        os.makedirs('reports', exist_ok=True)
        
        # Start task
        task = generate_monthly_report.delay()
        
        if not task.id:
            raise Exception("Failed to start task")
            
        return jsonify({
            'status': 'SUCCESS',
            'message': 'Report generation started',
            'task_id': task.id
        })
    except Exception as e:
        app.logger.error(f"Error triggering report: {str(e)}")
        return jsonify({
            'status': 'ERROR',
            'error': str(e)
        }), 500

@app.route('/api/admin/trigger-backup')
@roles_required('admin')
def trigger_backup():
    """Manually trigger database backup"""
    try:
        # Create necessary directories if they don't exist
        os.makedirs('backups', exist_ok=True)
        
        # Start the task
        task = backup_database.delay()
        app.logger.info(f"Started backup task: {task.id}")
        
        return jsonify({
            'message': 'Backup started',
            'task_id': task.id
        })
    except Exception as e:
        app.logger.error(f"Error triggering backup: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/export-analytics')
@roles_required('admin')
def trigger_analytics_export():
    """Manually trigger analytics export"""
    try:
        # Create necessary directories if they don't exist
        os.makedirs('exports', exist_ok=True)
        
        # Start the task
        task = export_analytics.delay()
        app.logger.info(f"Started analytics export task: {task.id}")
        
        return jsonify({
            'message': 'Analytics export started',
            'task_id': task.id
        })
    except Exception as e:
        app.logger.error(f"Error triggering analytics export: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/task-status/<task_id>')
@roles_required('admin')
def get_task_status(task_id):
    """Check status of a Celery task"""
    try:
        from celery.result import AsyncResult
        task = AsyncResult(task_id)
        
        response = {
            'task_id': task_id,
            'state': task.state,
            'info': None
        }
        
        if task.state == 'PENDING':
            response['info'] = 'Task is pending...'
        elif task.state == 'SUCCESS':
            response['info'] = task.get()
        elif task.state == 'FAILURE':
            response['info'] = str(task.result)
        else:
            response['info'] = 'Task is in progress...'
            
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Error checking task status: {str(e)}")
        return jsonify({
            'status': 'ERROR',
            'error': str(e)
        }), 500

# ------------- Student Quiz API Routes -------------
@app.route('/student/quiz/<int:quiz_id>')
@roles_required('stud')
def take_quiz(quiz_id):
    try:
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        
        quiz = Quiz.query.get_or_404(quiz_id)
        now = datetime.now()
        
        # Check if quiz is active
        if not quiz.start_time <= now <= quiz.end_time:
            return redirect(url_for('student_quizzes'))
            
        return render_template('student/templates/quiz.html', quiz=quiz)
    except Exception as e:
        app.logger.error(f"Error accessing quiz: {str(e)}")
        return redirect(url_for('student_quizzes'))

@app.route('/api/student/quiz/<int:quiz_id>', methods=['GET'])
@roles_required('stud')
def get_quiz_details(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if quiz is active
    if not quiz.is_active:
        return jsonify({'error': 'Quiz is not currently available'}), 403
        
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return jsonify({
        'id': quiz.id,
        'title': quiz.title,
        'duration': quiz.duration,
        'start_time': quiz.start_time.isoformat() if quiz.start_time else None,
        'end_time': quiz.end_time.isoformat() if quiz.end_time else None,
        'questions': [{
            'id': q.id,
            'text': q.question_text,
            'options': q.options,
            'marks': q.marks
        } for q in questions]
    })

@app.route('/api/student/quiz/<int:quiz_id>/submit', methods=['POST'])
@roles_required('stud')
def submit_quiz(quiz_id):
    from datetime import datetime
    
    try:
        data = request.get_json()
        if not data or 'answers' not in data:
            return jsonify({'error': 'No answers provided'}), 400
            
        quiz = Quiz.query.get_or_404(quiz_id)
        
        # Check if quiz is still active
        if not quiz.is_active:
            return jsonify({'error': 'Quiz has expired'}), 403
            
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        total_marks = sum(q.marks for q in questions)
        scored_marks = 0
        response_sheet = []
        
        for q in questions:
            question_id = str(q.id)
            submitted_index = data['answers'].get(question_id)
            is_correct = False
            user_answer_text = None
            
            if submitted_index is not None:
                try:
                    submitted_index = int(submitted_index)
                    if 0 <= submitted_index < len(q.options):
                        user_answer_text = q.options[submitted_index]
                        is_correct = (submitted_index == q.correct_answer)
                        if is_correct:
                            scored_marks += q.marks
                except (ValueError, TypeError) as e:
                    app.logger.error(f"Error processing answer: {e}")
            
            response_sheet.append({
                'question_id': q.id,
                'question_text': q.question_text,
                'options': q.options,
                'correct_answer': q.options[q.correct_answer],
                'user_answer': user_answer_text,
                'is_correct': is_correct,
                'marks': q.marks,
                'scored_marks': q.marks if is_correct else 0
            })
        
        score_percentage = (scored_marks / total_marks) * 100 if total_marks > 0 else 0
        
        # Save attempt with start and completion times
        attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=score_percentage,
            answers=data['answers'],
            response_sheet=response_sheet,
            started_at=datetime.utcnow(),  # Add this
            completed_at=datetime.utcnow()
        )
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({
            'score': score_percentage,
            'total_marks': total_marks,
            'scored_marks': scored_marks,
            'attempt_id': attempt.id,
            'questions': response_sheet
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error submitting quiz: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to submit quiz. Please try again.'}), 500

@app.route('/api/student/available-quizzes')
@roles_required('stud')
@cache.cached(timeout=60)  # Cache available quizzes for 1 minute
def get_available_quizzes():
    """Get all available quizzes for students"""
    try:
        now = datetime.now()  # Use system time
        quizzes = db.session.query(Quiz)\
            .join(Chapter)\
            .join(Subject)\
            .filter(
                Quiz.start_time <= now,
                Quiz.end_time >= now
            ).all()
        
        return jsonify([{
            'id': q.id,
            'title': q.title,
            'duration': q.duration,
            'description': q.description,
            'questions_count': len(q.questions),
            'chapter_name': q.chapter.name,
            'subject_name': q.chapter.subject.name,
            'chapter_id': q.chapter_id,
            'subject_id': q.chapter.subject_id,
            'start_time': q.start_time.isoformat(),
            'end_time': q.end_time.isoformat(),
            'remaining_time': int((q.end_time - now).total_seconds() / 60),
            'status': 'active'
        } for q in quizzes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------- Student Performance API Routes -------------
@app.route('/api/student/stats')
@roles_required('stud')
@cache.memoize(timeout=300)  # Cache per-user stats for 5 minutes
def get_student_stats():
    try:
        user_id = current_user.id
        
        # Get total attempts
        total_attempts = QuizAttempt.query.filter_by(user_id=user_id).count()
        
        # Get average score
        from sqlalchemy import func
        avg_score = db.session.query(func.avg(QuizAttempt.score))\
            .filter_by(user_id=user_id).scalar() or 0
        
        # Get recent performance (last 5 quizzes)
        recent_attempts = QuizAttempt.query.join(Quiz)\
            .filter(QuizAttempt.user_id == user_id)\
            .order_by(QuizAttempt.date_created.desc())\
            .limit(5)\
            .all()
            
        recent_performance = [{
            'quiz_title': attempt.quiz.title,
            'score': attempt.score,
            'date': attempt.date_created.strftime('%Y-%m-%d %H:%M')
        } for attempt in recent_attempts]
        
        # Get subject-wise performance
        subject_performance = db.session.query(
            Subject.name,
            func.avg(QuizAttempt.score).label('avg_score'),
            func.count(QuizAttempt.id).label('attempts')
        ).join(Quiz, QuizAttempt.quiz_id == Quiz.id)\
         .join(Chapter)\
         .join(Subject)\
         .filter(QuizAttempt.user_id == user_id)\
         .group_by(Subject.name)\
         .all()
         
        return jsonify({
            'totalAttempts': total_attempts,
            'averageScore': round(float(avg_score), 1),
            'recentPerformance': recent_performance,
            'subjectPerformance': [{
                'subject': row[0],
                'avgScore': round(float(row[1]), 1),
                'attempts': row[2]
            } for row in subject_performance]
        })
    except Exception as e:
        app.logger.error(f"Error getting student stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ------------- Student Quiz Attempts API Routes -------------
@app.route('/api/student/attempts')
@roles_required('stud')
def get_student_attempts():
    """Get all quiz attempts for the current student"""
    try:
        # Debug logging
        app.logger.info(f"Fetching attempts for user {current_user.id}")
        
        attempts = db.session.query(
            QuizAttempt,
            Quiz.title.label('quiz_title'),
            Subject.name.label('subject_name'),
            Chapter.name.label('chapter_name')
        ).join(
            Quiz, QuizAttempt.quiz_id == Quiz.id
        ).join(
            Chapter, Quiz.chapter_id == Chapter.id
        ).join(
            Subject, Chapter.subject_id == Subject.id
        ).filter(
            QuizAttempt.user_id == current_user.id
        ).order_by(
            QuizAttempt.date_created.desc()
        ).all()
        
        app.logger.info(f"Found {len(attempts)} attempts")
        
        # Calculate statistics
        total_attempts = len(attempts)
        if total_attempts > 0:
            avg_score = sum(a[0].score for a in attempts) / total_attempts
            passing_attempts = sum(1 for a in attempts if a[0].score >= 40)
            pass_rate = (passing_attempts / total_attempts) * 100
            app.logger.info(f"Stats: avg={avg_score:.1f}, pass_rate={pass_rate:.1f}%")
        else:
            avg_score = 0
            pass_rate = 0
        
        response_data = {
            'attempts': [{
                'id': a.QuizAttempt.id,
                'quiz_id': a.QuizAttempt.quiz_id,
                'quiz_title': a.quiz_title,
                'subject_name': a.subject_name,
                'chapter_name': a.chapter_name,
                'score': float(a.QuizAttempt.score),
                'date': a.QuizAttempt.date_created.isoformat(),
                'response_sheet': a.QuizAttempt.response_sheet
            } for a in attempts],
            'stats': {
                'averageScore': round(float(avg_score), 1),
                'totalAttempts': total_attempts,
                'passRate': round(float(pass_rate), 1)
            }
        }
        
        app.logger.debug(f"Sending response: {response_data}")
        return jsonify(response_data)
    except Exception as e:
        app.logger.error(f"Error getting student attempts: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/student/attempts/<int:attempt_id>')
@roles_required('stud')
def get_attempt_details(attempt_id):
    """Get detailed results for a specific quiz attempt"""
    try:
        app.logger.info(f"Fetching attempt details for ID: {attempt_id}")
        
        # Include all necessary relationships in one query
        attempt = QuizAttempt.query\
            .options(db.joinedload(QuizAttempt.quiz))\
            .filter(
                QuizAttempt.id == attempt_id,
                QuizAttempt.user_id == current_user.id
            ).first()
        
        if not attempt:
            app.logger.error(f"Attempt {attempt_id} not found or unauthorized")
            return jsonify({'error': 'Attempt not found'}), 404
        
        app.logger.debug(f"Found attempt: {attempt.id}, Score: {attempt.score}")
        app.logger.debug(f"Response sheet: {attempt.response_sheet}")
        
        # Build response data
        response_data = {
            'id': attempt.id,
            'quiz_title': attempt.quiz.title,
            'subject_name': attempt.quiz.chapter.subject.name,
            'chapter_name': attempt.quiz.chapter.name,
            'score': float(attempt.score),
            'date': attempt.date_created.isoformat(),
            'duration': attempt.duration,
            'started_at': attempt.started_at.isoformat() if attempt.started_at else None,
            'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
            'total_questions': len(attempt.quiz.questions),
            'response_sheet': attempt.response_sheet or [],
            'correct_answers': sum(1 for q in attempt.response_sheet if q.get('is_correct', False)) if attempt.response_sheet else 0
        }
        
        return jsonify(response_data)
    except Exception as e:
        app.logger.error(f"Error getting attempt details: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to load attempt details'}), 500

# ------------- Helper Functions -------------
def get_subject_wise_performance(user_id):
    """Helper function to get subject-wise performance stats"""
    from sqlalchemy import func
    subject_stats = db.session.query(
        Subject.name,
        func.count(QuizAttempt.id).label('attempts'),
        func.avg(QuizAttempt.score).label('avg_score'),
        func.sum(case((QuizAttempt.score >= 40, 1), else_=0)).label('passed')
    ).join(Quiz, QuizAttempt.quiz_id == Quiz.id)\
     .join(Chapter)\
     .join(Subject)\
     .filter(QuizAttempt.user_id == user_id)\
     .group_by(Subject.name)\
     .all()
    
    return [{
        'subject': stat[0],
        'attempts': stat[1],
        'avgScore': round(float(stat[2] or 0), 1),
        'passRate': round((stat[3] / stat[1]) * 100, 1) if stat[1] > 0 else 0
    } for stat in subject_stats]

@app.route('/api/student/all-quizzes')
@roles_required('stud')
def get_all_student_quizzes():
    """Get all quizzes categorized by status for students"""
    try:
        now = datetime.now()
        quizzes = db.session.query(Quiz)\
            .join(Chapter)\
            .join(Subject)\
            .all()
        
        upcoming = []
        ongoing = []
        expired = []
        
        for q in quizzes:
            quiz_data = {
                'id': q.id,
                'title': q.title,
                'duration': q.duration,
                'description': q.description,
                'questions_count': len(q.questions),
                'chapter_name': q.chapter.name,
                'subject_name': q.chapter.subject.name,
                'chapter_id': q.chapter_id,
                'subject_id': q.chapter.subject_id,
                'start_time': q.start_time.strftime('%Y-%m-%d %H:%M') if q.start_time else None,
                'end_time': q.end_time.strftime('%Y-%m-%d %H:%M') if q.end_time else None
            }
            
            if q.start_time and q.end_time:
                if q.start_time <= now <= q.end_time:
                    quiz_data['remaining_time'] = int((q.end_time - now).total_seconds() / 60)
                    ongoing.append(quiz_data)
                elif now < q.start_time:
                    quiz_data['time_until_start'] = int((q.start_time - now).total_seconds() / 60)
                    upcoming.append(quiz_data)
                else:
                    expired.append(quiz_data)
        
        return jsonify({
            'upcoming': upcoming,
            'ongoing': ongoing,
            'expired': expired
        })
    except Exception as e:
        app.logger.error(f"Error in get_all_student_quizzes: {str(e)}")
        return jsonify({'error': str(e)}), 500
