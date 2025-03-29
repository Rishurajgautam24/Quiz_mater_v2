new Vue({
    el: '#app',
    
    // --------------- Data Management --------------- 
    data: {
        // User info
        username: '',               // Stores logged-in username
        
        // Content management
        subjects: [],              // List of all subjects
        chaptersForQuiz: [],       // List of chapters for selected subject
        quizzes: [],              // List of quizzes for selected chapter
        questions: [],            // List of questions for selected quiz
        
        // Selection tracking
        selectedSubjectId: '',     // Currently selected subject ID
        selectedChapterId: '',     // Currently selected chapter ID
        selectedQuizId: null,      // Currently selected quiz ID
        
        // Modal states
        showQuizModal: false,
        showQuestionModal: false,
        
        // Editing states
        editingQuiz: null,         // Quiz being edited
        editingQuestion: null,     // Question being edited
        
        // Form data
        quizForm: {
            title: '',
            description: '',
            duration_hours: 0,
            duration_minutes: 30,
            start_time: null,
            chapter_id: null
        },
        questionForm: {
            question_text: '',
            options: ['', ''],
            correct_answer: null,
            marks: 1
        },
        
        // UI states
        error: null,               // Error message storage
        selectedSubject: '',       // Selected subject name
        selectedChapter: '',       // Selected chapter name
    },
    
    // --------------- Methods --------------- 
    methods: {
        // --------------- Data Loading Methods --------------- 
        fetchSubjects() {
            axios.get('/api/subjects')
                .then(response => this.subjects = response.data)
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error fetching subjects';
                    setTimeout(() => this.error = null, 5000); // Auto-dismiss after 5 seconds
                });
        },

        loadChaptersForQuiz() {
            if (this.selectedSubjectId) {
                const subject = this.subjects.find(s => s.id === parseInt(this.selectedSubjectId));
                this.selectedSubject = subject ? subject.name : '';
                
                axios.get(`/api/subjects/${this.selectedSubjectId}/chapters`)
                    .then(response => {
                        this.chaptersForQuiz = response.data;
                        this.selectedChapterId = '';
                        this.selectedChapter = '';
                        this.quizzes = [];
                        this.selectedQuizId = null;
                        this.questions = [];
                    })
                    .catch(error => {
                        this.error = error.response?.data?.message || 'Error loading chapters';
                        setTimeout(() => this.error = null, 5000);
                    });
            } else {
                this.chaptersForQuiz = [];
                this.selectedChapterId = '';
                this.selectedSubject = '';
                this.selectedChapter = '';
                this.quizzes = [];
                this.questions = [];
            }
        },

        loadQuizzes() {
            if (this.selectedChapterId) {
                const chapter = this.chaptersForQuiz.find(c => c.id === parseInt(this.selectedChapterId));
                this.selectedChapter = chapter ? chapter.name : '';
                
                axios.get(`/api/chapters/${this.selectedChapterId}/quizzes`)
                    .then(response => {
                        this.quizzes = response.data;
                        this.selectedQuizId = null;
                        this.questions = [];
                    })
                    .catch(error => {
                        this.error = error.response?.data?.message || 'Error loading quizzes';
                        setTimeout(() => this.error = null, 5000);
                    });
            } else {
                this.quizzes = [];
                this.selectedChapter = '';
                this.questions = [];
            }
        },

        // Add logout method
        logout() {
            axios.post('/api/logout')
                .then(() => window.location.href = '/')
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error logging out';
                    setTimeout(() => this.error = null, 5000);
                });
        },

        // --------------- Quiz Management Methods --------------- 
        openQuizModal() {
            if (!this.selectedChapterId) {
                this.error = 'Please select a chapter first';
                setTimeout(() => this.error = null, 5000);
                return;
            }
            this.editingQuiz = null;
            
            // Get current system time in format for datetime-local input
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const defaultStartTime = `${year}-${month}-${day}T${hours}:${minutes}`;
            
            this.quizForm = {
                title: '',
                description: '',
                duration_hours: 0,
                duration_minutes: 30,
                start_time: defaultStartTime,
                chapter_id: this.selectedChapterId
            };
            this.showQuizModal = true;
            document.body.classList.add('modal-open');
            document.body.style.overflow = 'hidden';
        },

        closeQuizModal() {
            this.showQuizModal = false;
            this.editingQuiz = null;
            this.quizForm = {
                title: '',
                description: '',
                duration_hours: 0,
                duration_minutes: 30,
                start_time: null,
                chapter_id: null
            };
            document.body.classList.remove('modal-open');
            document.body.style.overflow = 'auto';
        },

        async saveQuiz() {
            try {
                if (!this.quizForm.title) {
                    this.error = 'Title is required';
                    return;
                }

                // Calculate total duration in minutes
                const durationHours = parseInt(this.quizForm.duration_hours) || 0;
                const durationMinutes = parseInt(this.quizForm.duration_minutes) || 0;
                const totalDuration = (durationHours * 60) + durationMinutes;
                
                if (totalDuration <= 0) {
                    this.error = 'Quiz duration must be greater than 0';
                    return;
                }

                const formData = {
                    title: this.quizForm.title,
                    description: this.quizForm.description,
                    chapter_id: this.selectedChapterId,
                    duration: totalDuration
                };
                
                // Send start time with timezone information
                if (this.quizForm.start_time) {
                    // Just send the datetime-local value directly
                    formData.start_time = this.quizForm.start_time;
                } else {
                    // Format current time in local timezone
                    const now = new Date();
                    const year = now.getFullYear();
                    const month = String(now.getMonth() + 1).padStart(2, '0');
                    const day = String(now.getDate()).padStart(2, '0');
                    const hours = String(now.getHours()).padStart(2, '0');
                    const minutes = String(now.getMinutes()).padStart(2, '0');
                    formData.start_time = `${year}-${month}-${day}T${hours}:${minutes}`;
                }

                const url = this.editingQuiz ? `/api/quizzes/${this.editingQuiz.id}` : '/api/quizzes';
                const method = this.editingQuiz ? 'PUT' : 'POST';

                await axios({
                    method: method,
                    url: url,
                    data: formData
                });

                this.closeQuizModal();
                await this.loadQuizzes();
                this.error = null;
            } catch (error) {
                console.error('Error saving quiz:', error);
                this.error = error.response?.data?.error || 'Failed to save quiz';
            }
        },

        editQuiz(quiz) {
            this.editingQuiz = quiz;
            const hours = Math.floor(quiz.duration / 60);
            const minutes = quiz.duration % 60;
            
            // Parse UTC time from server and adjust to local timezone for the input
            let startTime = '';
            if (quiz.start_time) {
                const date = new Date(quiz.start_time);
                // Format for datetime-local input (YYYY-MM-DDTHH:MM)
                // This automatically converts to local timezone
                startTime = date.toISOString().slice(0, 16);
            }
            
            this.quizForm = {
                title: quiz.title,
                description: quiz.description || '',
                duration_hours: hours,
                duration_minutes: minutes,
                start_time: startTime,
                chapter_id: quiz.chapter_id
            };
            this.showQuizModal = true;
            document.body.classList.add('modal-open');
            document.body.style.overflow = 'hidden';
        },

        deleteQuiz(id) {
            if (confirm('Are you sure you want to delete this quiz?')) {
                axios.delete(`/api/quizzes/${id}`)
                    .then(response => {
                        // Remove quiz from local list
                        this.quizzes = this.quizzes.filter(q => q.id !== id);
                        this.selectedQuizId = null;
                        this.questions = [];
                        this.error = null;
                        
                        // Show success message
                        this.error = 'Quiz deleted successfully';
                        setTimeout(() => this.error = null, 3000);
                    })
                    .catch(error => {
                        console.error('Error deleting quiz:', error);
                        this.error = error.response?.data?.error || 'Failed to delete quiz';
                        setTimeout(() => this.error = null, 5000);
                    });
            }
        },

        showQuestions(quiz) {
            // Toggle behavior: if clicking the same quiz, close it
            if (this.selectedQuizId === quiz.id) {
                this.selectedQuizId = null;
                this.questions = [];
            } else {
                this.selectedQuizId = quiz.id;
                this.fetchQuestions(quiz.id);
            }
        },

        fetchQuestions(quizId) {
            axios.get(`/api/quizzes/${quizId}/questions`)
                .then(response => this.questions = response.data)
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error fetching questions';
                    setTimeout(() => this.error = null, 5000);
                });
        },

        // --------------- Question Management Methods --------------- 
        openQuestionModal() {
            if (!this.selectedQuizId) {
                this.error = 'Please select a quiz first';
                setTimeout(() => this.error = null, 5000);
                return;
            }
            this.editingQuestion = null;
            this.questionForm = {
                question_text: '',
                options: ['', ''],
                correct_answer: null,
                marks: 1
            };
            this.showQuestionModal = true;
            document.body.classList.add('modal-open');
        },

        closeQuestionModal() {
            this.showQuestionModal = false;
            this.editingQuestion = null;
            this.questionForm = {
                question_text: '',
                options: ['', ''],
                correct_answer: null,
                marks: 1
            };
            document.body.classList.remove('modal-open');
        },

        saveQuestion() {
            const method = this.editingQuestion ? 'put' : 'post';
            const url = this.editingQuestion ? 
                `/api/questions/${this.editingQuestion.id}` : '/api/questions';
            
            const data = {
                ...this.questionForm,
                quiz_id: this.selectedQuizId
            };

            axios[method](url, data)
                .then(() => {
                    this.closeQuestionModal();
                    this.fetchQuestions(this.selectedQuizId);
                })
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error saving question';
                    setTimeout(() => this.error = null, 5000);
                });
        },

        editQuestion(question) {
            this.editingQuestion = question;
            this.questionForm = {
                question_text: question.question_text,
                options: [...question.options],
                correct_answer: question.correct_answer,
                marks: question.marks
            };
            this.showQuestionModal = true;
            document.body.classList.add('modal-open');
        },

        deleteQuestion(id) {
            if (confirm('Are you sure you want to delete this question?')) {
                axios.delete(`/api/questions/${id}`)
                    .then(() => this.fetchQuestions(this.selectedQuizId))
                    .catch(error => {
                        this.error = error.response?.data?.message || 'Error deleting question';
                        setTimeout(() => this.error = null, 5000);
                    });
            }
        },

        addOption() {
            if (this.questionForm.options.length < 6) {
                this.questionForm.options.push('');
            }
        },

        removeOption(index) {
            if (this.questionForm.options.length > 2) {
                this.questionForm.options.splice(index, 1);
                if (this.questionForm.correct_answer === index) {
                    this.questionForm.correct_answer = null;
                } else if (this.questionForm.correct_answer > index) {
                    // Adjust correct answer index if we removed an option before it
                    this.questionForm.correct_answer--;
                }
            }
        },

        showSection(section) {
            if (section === 'users') {
                window.location.href = '/admin/user-management';
            } else if (section === 'reports') {
                window.location.href = '/admin/reports';
            }
        },

        // Close modals on escape key
        closeModalOnEscape(e) {
            if (e.key === 'Escape') {
                if (this.showQuizModal) this.closeQuizModal();
                if (this.showQuestionModal) this.closeQuestionModal();
            }
        },

        formatDateTime(dateStr) {
            if (!dateStr) return '';
            
            // Simple date and time formatting
            const date = new Date(dateStr);
            const options = { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit', 
                minute: '2-digit',
                hour12: true
            };
            return date.toLocaleString(undefined, options);
        },

        getStatusBadgeClass(quiz) {
            // Use local time for comparison with server times
            const now = new Date();
            const start = quiz.start_time ? new Date(quiz.start_time) : null;
            const end = quiz.end_time ? new Date(quiz.end_time) : null;
            
            if (!start || !end) return 'bg-secondary';
            if (now < start) return 'bg-info';
            if (now > end) return 'bg-danger';
            return 'bg-success';
        }
    },
    
    // --------------- Lifecycle Hooks --------------- 
    mounted() {
        this.fetchSubjects();
        // Get username for display
        this.username = document.querySelector('meta[name="username"]')?.content || '';
        // Add keyboard listener for modal escape
        document.addEventListener('keydown', this.closeModalOnEscape);
        // Make Vue instance available for debugging
        window.app = this;
    },
    
    beforeDestroy() {
        document.removeEventListener('keydown', this.closeModalOnEscape);
    }
});
