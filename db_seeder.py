from application.models import db, Subject, Chapter, Quiz, Question, User, Role
from flask_security import hash_password
from uuid import uuid4
from flask import Flask
from main import create_app
from datetime import datetime, timedelta

def seed_database():
    print("Starting database seeding...")
    
    # Clear existing data
    Question.query.delete()
    Quiz.query.delete()
    Chapter.query.delete()
    Subject.query.delete()
    
    # ----- Create Subjects -----
    subjects = [
        {"name": "Computer Science", "description": "Study of computers and computing technologies"},
        {"name": "Mathematics", "description": "Study of numbers, quantities, and shapes"},
        {"name": "Physics", "description": "Study of matter, energy, and the interactions between them"},
        {"name": "Chemistry", "description": "Study of substances, their properties, and reactions"}
    ]
    
    created_subjects = {}
    for subject_data in subjects:
        subject = Subject(**subject_data)
        db.session.add(subject)
        db.session.flush()  # Get the ID without committing
        created_subjects[subject.name] = subject
        
    print(f"Added {len(subjects)} subjects")
    
    # ----- Create Chapters -----
    chapters = {
        "Computer Science": [
            {"name": "Programming Fundamentals", "description": "Basic concepts of programming"},
            {"name": "Data Structures", "description": "Fundamental data structures and algorithms"},
            {"name": "Database Systems", "description": "Principles of database management"},
            {"name": "Web Development", "description": "Concepts of web development"}
        ],
        "Mathematics": [
            {"name": "Algebra", "description": "Study of mathematical symbols and rules"},
            {"name": "Calculus", "description": "Study of continuous change"},
            {"name": "Statistics", "description": "Analysis and interpretation of data"}
        ],
        "Physics": [
            {"name": "Mechanics", "description": "Study of motion and forces"},
            {"name": "Thermodynamics", "description": "Energy and heat transfer"},
            {"name": "Electromagnetism", "description": "Study of electrical and magnetic phenomena"}
        ],
        "Chemistry": [
            {"name": "Organic Chemistry", "description": "Study of carbon compounds"},
            {"name": "Inorganic Chemistry", "description": "Study of non-carbon compounds"},
            {"name": "Physical Chemistry", "description": "Application of physics to chemical systems"}
        ]
    }
    
    created_chapters = {}
    for subject_name, chapter_list in chapters.items():
        subject = created_subjects[subject_name]
        for chapter_data in chapter_list:
            chapter = Chapter(subject_id=subject.id, **chapter_data)
            db.session.add(chapter)
            db.session.flush()
            key = f"{subject_name}:{chapter.name}"
            created_chapters[key] = chapter
    
    print(f"Added {sum(len(c) for c in chapters.values())} chapters")
    
    # ----- Create Quizzes -----
    # Get current time for quiz scheduling
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)
    next_week = now + timedelta(days=7)
    
    quizzes = {
        "Computer Science:Programming Fundamentals": [
            {
                "title": "Python Basics", 
                "description": "Test your knowledge of Python fundamentals", 
                "duration": 30,
                "start_time": yesterday,
                "end_time": yesterday + timedelta(hours=2)  # Expired quiz
            },
            {
                "title": "Control Structures", 
                "description": "Quiz on loops and conditionals", 
                "duration": 20,
                "start_time": now,
                "end_time": now + timedelta(hours=24)  # Currently active quiz
            }
        ],
        "Computer Science:Data Structures": [
            {
                "title": "Arrays and Lists", 
                "description": "Quiz on array operations", 
                "duration": 25,
                "start_time": now - timedelta(hours=1),
                "end_time": now + timedelta(hours=5)  # Currently active quiz
            },
            {
                "title": "Trees and Graphs", 
                "description": "Advanced data structures", 
                "duration": 35,
                "start_time": tomorrow,
                "end_time": tomorrow + timedelta(hours=48)  # Future quiz
            }
        ],
        "Mathematics:Algebra": [
            {
                "title": "Linear Equations", 
                "description": "Solving linear equations", 
                "duration": 30,
                "start_time": now,
                "end_time": now + timedelta(hours=12)  # Currently active quiz
            },
            {
                "title": "Quadratic Equations", 
                "description": "Solving quadratic equations", 
                "duration": 35,
                "start_time": next_week,
                "end_time": next_week + timedelta(hours=24)  # Future quiz
            }
        ],
        "Physics:Mechanics": [
            {
                "title": "Newton's Laws", 
                "description": "Test on principles of motion", 
                "duration": 25,
                "start_time": now - timedelta(hours=2),
                "end_time": now + timedelta(hours=1)  # Currently active quiz
            },
            {
                "title": "Kinematics", 
                "description": "Quiz on motion equations", 
                "duration": 30,
                "start_time": tomorrow,
                "end_time": tomorrow + timedelta(hours=3)  # Future quiz
            }
        ],
        "Chemistry:Organic Chemistry": [
            {
                "title": "Functional Groups", 
                "description": "Identifying organic functional groups", 
                "duration": 20,
                "start_time": now,
                "end_time": now + timedelta(hours=2)  # Currently active quiz
            },
            {
                "title": "Reaction Mechanisms", 
                "description": "Organic reaction pathways", 
                "duration": 40,
                "start_time": None,  # Draft quiz (no schedule yet)
                "end_time": None
            }
        ]
    }
    
    created_quizzes = {}
    for chapter_key, quiz_list in quizzes.items():
        chapter = created_chapters[chapter_key]
        for quiz_data in quiz_list:
            quiz = Quiz(chapter_id=chapter.id, **quiz_data)
            db.session.add(quiz)
            db.session.flush()
            key = f"{chapter_key}:{quiz.title}"
            created_quizzes[key] = quiz
    
    print(f"Added {sum(len(q) for q in quizzes.values())} quizzes with scheduling")
    
    # ----- Create Questions -----
    questions = {
        "Computer Science:Programming Fundamentals:Python Basics": [
            {
                "question_text": "What is the output of print(2 + 2)?",
                "options": ["2", "4", "22", "Error"],
                "correct_answer": 1,  # Index 1 which is "4"
                "marks": 1
            },
            {
                "question_text": "Which of the following is a mutable data type in Python?",
                "options": ["string", "tuple", "list", "int"],
                "correct_answer": 2,  # Index 2 which is "list"
                "marks": 1
            },
            {
                "question_text": "What does the len() function do?",
                "options": ["Returns the largest item in an iterable", "Returns the length of an object", "Returns the lowest item in an iterable", "Returns the sum of all items"],
                "correct_answer": 1,
                "marks": 1
            },
            # Added questions
            {
                "question_text": "Which of these is NOT a Python built-in data type?",
                "options": ["list", "dictionary", "array", "tuple"],
                "correct_answer": 2,  # array
                "marks": 1
            },
            {
                "question_text": "How do you create a comment in Python?",
                "options": ["// comment", "/* comment */", "# comment", "<!-- comment -->"],
                "correct_answer": 2,  # # comment
                "marks": 1
            },
            {
                "question_text": "What is the correct way to create a function in Python?",
                "options": ["function myFunc():", "def myFunc():", "create myFunc():", "void myFunc():"],
                "correct_answer": 1,  # def myFunc():
                "marks": 1
            },
            {
                "question_text": "Which method is used to add an element to a list in Python?",
                "options": ["add()", "append()", "insert()", "extend()"],
                "correct_answer": 1,  # append()
                "marks": 1
            },
            {
                "question_text": "What does the 'self' parameter refer to in a class method?",
                "options": ["Current module", "Current function", "Current class", "Current instance"],
                "correct_answer": 3,  # Current instance
                "marks": 1
            },
            {
                "question_text": "What is the output of 'Hello' + 'World'?",
                "options": ["Hello World", "HelloWorld", "Error", "Hello + World"],
                "correct_answer": 1,  # HelloWorld
                "marks": 1
            },
            {
                "question_text": "Which of the following is used to handle exceptions in Python?",
                "options": ["if-else", "try-except", "for-in", "while-do"],
                "correct_answer": 1,  # try-except
                "marks": 1
            }
        ],
        "Computer Science:Programming Fundamentals:Control Structures": [
            {
                "question_text": "Which of the following is not a loop structure in Python?",
                "options": ["for", "while", "do-while", "foreach"],
                "correct_answer": 2,  # do-while
                "marks": 1
            },
            {
                "question_text": "What keyword is used to exit a loop prematurely?",
                "options": ["exit", "break", "stop", "continue"],
                "correct_answer": 1,  # break
                "marks": 1
            },
            {
                "question_text": "Which statement skips the current iteration of a loop?",
                "options": ["skip", "pass", "continue", "next"],
                "correct_answer": 2,  # continue
                "marks": 1
            },
            {
                "question_text": "What is the output of: for i in range(3): print(i)",
                "options": ["0 1 2", "1 2 3", "0 1 2 3", "Error"],
                "correct_answer": 0,  # 0 1 2
                "marks": 1
            },
            {
                "question_text": "Which is the correct way to write an if-else statement in Python?",
                "options": ["if (condition) {code} else {code}", "if condition: code else: code", "if condition then code else code", "if: condition else: condition"],
                "correct_answer": 1,  # if condition: code else: code
                "marks": 1
            },
            {
                "question_text": "What does the 'elif' keyword mean?",
                "options": ["End loop if", "Else if", "End life if", "Evaluate loop if"],
                "correct_answer": 1,  # Else if
                "marks": 1
            },
            {
                "question_text": "What value is considered falsy in Python?",
                "options": ["1", "True", "'0'", "[]"],
                "correct_answer": 3,  # []
                "marks": 1
            },
            {
                "question_text": "Which operator is used for logical AND in Python?",
                "options": ["&", "&&", "and", "AND"],
                "correct_answer": 2,  # and
                "marks": 1
            },
            {
                "question_text": "What happens if the condition in a while loop is always True?",
                "options": ["The code runs once", "The code never runs", "Infinite loop", "Syntax error"],
                "correct_answer": 2,  # Infinite loop
                "marks": 1
            },
            {
                "question_text": "What is the main purpose of a loop?",
                "options": ["To make programs faster", "To repeat code blocks", "To handle exceptions", "To improve code readability"],
                "correct_answer": 1,  # To repeat code blocks
                "marks": 1
            }
        ],
        "Computer Science:Data Structures:Arrays and Lists": [
            # Add 10 questions about arrays and lists
            {
                "question_text": "What is the time complexity of accessing an element in an array by index?",
                "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
                "correct_answer": 0,  # O(1)
                "marks": 1
            },
            {
                "question_text": "Which operation is NOT constant time for Python lists?",
                "options": ["Appending an element", "Getting an element by index", "Inserting at a specific position", "Checking if list is empty"],
                "correct_answer": 2,  # Inserting at a specific position
                "marks": 1
            },
            {
                "question_text": "What method is used to sort a list in Python?",
                "options": ["list.sort()", "list.order()", "sorted(list)", "All of the above"],
                "correct_answer": 0,  # list.sort()
                "marks": 1
            },
            {
                "question_text": "What is the difference between append() and extend() methods?",
                "options": ["No difference", "append() adds one element, extend() adds multiple elements", "append() adds to end, extend() adds to beginning", "append() only works with numbers, extend() works with any type"],
                "correct_answer": 1,  # append() adds one element, extend() adds multiple elements
                "marks": 1
            },
            {
                "question_text": "How do you create a list comprehension in Python?",
                "options": ["[for x in range(10)]", "[x for x in range(10)]", "for x in range(10): [x]", "(x for x in range(10))"],
                "correct_answer": 1,  # [x for x in range(10)]
                "marks": 1
            },
            {
                "question_text": "What happens when you slice a list with negative indices?",
                "options": ["Error occurs", "Counts from beginning of list", "Counts from end of list", "Returns empty list"],
                "correct_answer": 2,  # Counts from end of list
                "marks": 1
            },
            {
                "question_text": "Which data structure is more memory efficient, a list or a tuple?",
                "options": ["List", "Tuple", "Both use the same amount", "Depends on the content"],
                "correct_answer": 1,  # Tuple
                "marks": 1
            },
            {
                "question_text": "What does list.pop() do in Python?",
                "options": ["Removes first element", "Removes last element", "Removes random element", "Removes all elements"],
                "correct_answer": 1,  # Removes last element
                "marks": 1
            },
            {
                "question_text": "How do you check if an element exists in a list?",
                "options": ["element in list", "list.contains(element)", "list.has(element)", "element.exists(list)"],
                "correct_answer": 0,  # element in list
                "marks": 1
            },
            {
                "question_text": "What is the correct way to copy a list in Python?",
                "options": ["list2 = list1", "list2 = list1.copy()", "list2 = copy(list1)", "list2 == list1"],
                "correct_answer": 1,  # list2 = list1.copy()
                "marks": 1
            }
        ],
        "Mathematics:Algebra:Linear Equations": [
            {
                "question_text": "Solve for x: 3x + 5 = 14",
                "options": ["x = 3", "x = 4", "x = 5", "x = 6"],
                "correct_answer": 0,  # Index 0 which is "x = 3"
                "marks": 1
            },
            {
                "question_text": "Which of the following is a linear equation?",
                "options": ["y = x²", "y = 3x + 2", "y = 1/x", "y = √x"],
                "correct_answer": 1,  # Index 1 which is "y = 3x + 2"
                "marks": 1
            },
            # Added questions
            {
                "question_text": "What is the slope in the equation y = 2x + 3?",
                "options": ["2", "3", "2x", "x"],
                "correct_answer": 0,  # 2
                "marks": 1
            },
            {
                "question_text": "What is the y-intercept in the equation y = 5x - 7?",
                "options": ["5", "-7", "5x", "y"],
                "correct_answer": 1,  # -7
                "marks": 1
            },
            {
                "question_text": "Which equation represents a vertical line?",
                "options": ["y = 5", "x = 3", "y = 2x", "y = x + 1"],
                "correct_answer": 1,  # x = 3
                "marks": 1
            },
            {
                "question_text": "Solve the system: 2x + y = 5, x - y = 1",
                "options": ["x = 2, y = 1", "x = 1, y = 3", "x = 3, y = -1", "x = 0, y = 5"],
                "correct_answer": 0,  # x = 2, y = 1
                "marks": 1
            },
            {
                "question_text": "What does the point of intersection of two lines represent?",
                "options": ["The solution to their system of equations", "The midpoint of both lines", "The average slope", "None of the above"],
                "correct_answer": 0,  # The solution to their system of equations
                "marks": 1
            },
            {
                "question_text": "Which of these forms is NOT a way to write a linear equation?",
                "options": ["Slope-intercept form", "Point-slope form", "Standard form", "Quadratic form"],
                "correct_answer": 3,  # Quadratic form
                "marks": 1
            },
            {
                "question_text": "What is the slope of a horizontal line?",
                "options": ["0", "1", "Undefined", "Infinity"],
                "correct_answer": 0,  # 0
                "marks": 1
            },
            {
                "question_text": "If two lines have the same slope, they are:",
                "options": ["Perpendicular", "Parallel", "Intersecting", "Coincident"],
                "correct_answer": 1,  # Parallel
                "marks": 1
            }
        ],
        "Physics:Mechanics:Newton's Laws": [
            {
                "question_text": "Newton's First Law states that:",
                "options": [
                    "Force equals mass times acceleration", 
                    "An object at rest stays at rest unless acted upon by an external force", 
                    "For every action there is an equal and opposite reaction",
                    "Energy cannot be created or destroyed"
                ],
                "correct_answer": 1,
                "marks": 2
            },
            {
                "question_text": "What is the formula for Newton's Second Law?",
                "options": ["F = ma", "E = mc²", "F = G(m₁m₂)/r²", "p = mv"],
                "correct_answer": 0,  # Index 0 which is "F = ma"
                "marks": 1
            },
            # Added questions
            {
                "question_text": "Newton's Third Law is about:",
                "options": ["Inertia", "Acceleration", "Action and reaction", "Conservation of energy"],
                "correct_answer": 2,  # Action and reaction
                "marks": 1
            },
            {
                "question_text": "What is inertia?",
                "options": ["A force", "Resistance to change in motion", "Acceleration", "Velocity"],
                "correct_answer": 1,  # Resistance to change in motion
                "marks": 1
            },
            {
                "question_text": "Which of the following is a vector quantity?",
                "options": ["Mass", "Time", "Force", "Temperature"],
                "correct_answer": 2,  # Force
                "marks": 1
            },
            {
                "question_text": "What happens to acceleration if force is doubled and mass is halved?",
                "options": ["Stays the same", "Doubles", "Quadruples", "Halves"],
                "correct_answer": 2,  # Quadruples
                "marks": 1
            },
            {
                "question_text": "If an object is moving at constant velocity, what can be said about the net force on it?",
                "options": ["The net force is constant", "The net force is increasing", "The net force is zero", "The net force is decreasing"],
                "correct_answer": 2,  # The net force is zero
                "marks": 1
            },
            {
                "question_text": "Which law explains why you feel pushed back in your seat when a car accelerates forward?",
                "options": ["Newton's First Law", "Newton's Second Law", "Newton's Third Law", "Law of Conservation of Momentum"],
                "correct_answer": 0,  # Newton's First Law
                "marks": 1
            },
            {
                "question_text": "What is the SI unit of force?",
                "options": ["Watt", "Newton", "Joule", "Pascal"],
                "correct_answer": 1,  # Newton
                "marks": 1
            },
            {
                "question_text": "A rocket propels itself forward by:",
                "options": ["Pushing against the air", "Burning fuel", "Expelling gas backward (Newton's Third Law)", "Using magnetic repulsion"],
                "correct_answer": 2,  # Expelling gas backward (Newton's Third Law)
                "marks": 1
            }
        ],
        "Chemistry:Organic Chemistry:Functional Groups": [
            # 10 questions about functional groups
            {
                "question_text": "Which functional group is characterized by a carbon-oxygen double bond?",
                "options": ["Alcohol", "Ether", "Carbonyl", "Amine"],
                "correct_answer": 2,  # Carbonyl
                "marks": 1
            },
            {
                "question_text": "What is the functional group in alcohols?",
                "options": ["-COOH", "-OH", "-CO", "-NH2"],
                "correct_answer": 1,  # -OH
                "marks": 1
            },
            {
                "question_text": "Which functional group is present in carboxylic acids?",
                "options": ["-COOH", "-CHO", "-CO", "-COO-"],
                "correct_answer": 0,  # -COOH
                "marks": 1
            },
            {
                "question_text": "Amines contain which element bonded to carbon?",
                "options": ["Oxygen", "Nitrogen", "Sulfur", "Phosphorus"],
                "correct_answer": 1,  # Nitrogen
                "marks": 1
            },
            {
                "question_text": "What functional group is found in aldehydes?",
                "options": ["-OH", "-COOH", "-CHO", "-C=C-"],
                "correct_answer": 2,  # -CHO
                "marks": 1
            },
            {
                "question_text": "Esters are derivatives of which compounds?",
                "options": ["Alcohols and aldehydes", "Alcohols and carboxylic acids", "Amines and carboxylic acids", "Ketones and alcohols"],
                "correct_answer": 1,  # Alcohols and carboxylic acids
                "marks": 1
            },
            {
                "question_text": "The benzene ring is characteristic of which class of compounds?",
                "options": ["Aliphatic", "Aromatic", "Heterocyclic", "Alicyclic"],
                "correct_answer": 1,  # Aromatic
                "marks": 1
            },
            {
                "question_text": "Which functional group contains a carbon-nitrogen triple bond?",
                "options": ["Amine", "Amide", "Nitrile", "Nitro"],
                "correct_answer": 2,  # Nitrile
                "marks": 1
            },
            {
                "question_text": "What is the general formula for alkenes?",
                "options": ["CnH2n+2", "CnH2n", "CnH2n-2", "CnHn"],
                "correct_answer": 1,  # CnH2n
                "marks": 1
            },
            {
                "question_text": "Which functional group is responsible for the characteristic smell of perfumes?",
                "options": ["Alcohols", "Ethers", "Esters", "Ketones"],
                "correct_answer": 2,  # Esters
                "marks": 1
            }
        ]
    }
    
    for quiz_key, question_list in questions.items():
        quiz = created_quizzes[quiz_key]
        for question_data in question_list:
            question = Question(quiz_id=quiz.id, **question_data)
            db.session.add(question)
    
    print(f"Added {sum(len(q) for q in questions.values())} questions")
    
    # Create admin user if it doesn't exist
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrator')
        db.session.add(admin_role)
    
    stud_role = Role.query.filter_by(name='stud').first()
    if not stud_role:
        stud_role = Role(name='stud', description='Student')
        db.session.add(stud_role)
    
    admin_user = User.query.filter_by(email='admin@example.com').first()
    if not admin_user:
        admin_user = User(
            email='admin@example.com',
            username='admin',
            password=hash_password('admin123'),
            active=True,
            fs_uniquifier=str(uuid4())
        )
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
    
    student_user = User.query.filter_by(email='student@example.com').first()
    if not student_user:
        student_user = User(
            email='student@example.com',
            username='student',
            password=hash_password('student123'),
            active=True,
            fs_uniquifier=str(uuid4())
        )
        student_user.roles.append(stud_role)
        db.session.add(student_user)
    
    # Commit all changes
    db.session.commit()
    print("Database seeding completed successfully!")
    print("Quiz statuses:")
    for quiz in Quiz.query.all():
        print(f"- {quiz.title}: {quiz.status} (Start: {quiz.start_time}, End: {quiz.end_time})")

if __name__ == "__main__":
    # Create the Flask app context
    app, datastore = create_app()  # Modified to handle tuple return from main.py
    
    # Push an application context
    with app.app_context():
        seed_database()
