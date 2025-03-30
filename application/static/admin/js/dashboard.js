new Vue({
    el: '#app',
    
    // --------------- Data Management --------------- 
    data: {
        // User info
        username: '',           // Stores logged-in username
        
        // Content management
        subjects: [],          // List of all subjects
        chapters: [],          // List of chapters for selected subject
        quizzes: [],          // List of quizzes for selected chapter
        
        // Selection tracking
        selectedSubject: null, // Currently selected subject
        selectedChapter: null, // Currently selected chapter
        
        // Modal states
        showSubjectModal: false,
        showChapterModal: false,
        showBackdrop: false,
        
        // Editing states
        editingSubject: null,  // Subject being edited
        editingChapter: null,  // Chapter being edited
        
        // Form data
        subjectForm: {
            name: '',
            description: ''
        },
        chapterForm: {
            name: '',
            description: ''
        },
        
        // UI states
        currentSection: 'subjects', // Current view section
        error: null,               // Error message storage

        // Background task states
        taskInProgress: false,
        taskStatus: null,
        statusAlertClass: '',
        statusIconClass: '',
    },
    
    // --------------- Computed Properties --------------- 
    computed: {
        // Navigation section visibility controls
        showSubjectsSection() {
            return this.currentSection === 'subjects';
        },
        showUsersSection() {
            return this.currentSection === 'users';
        },
        showReportsSection() {
            return this.currentSection === 'reports';
        }
    },
    
    // --------------- Methods --------------- 
    methods: {
        // --------------- Authentication Methods --------------- 
        logout() {
            // Log out the user and redirect to the login page
            axios.post('/api/logout')
                .then(() => window.location.href = '/')
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error logging out';
                });
        },
        
        // --------------- Subject Operations --------------- 
        fetchSubjects() {
            // Retrieve all subjects from the API
            axios.get('/api/subjects')
                .then(response => this.subjects = response.data)
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error fetching subjects';
                    setTimeout(() => this.error = null, 5000); // Auto-dismiss after 5 seconds
                });
        },

        selectSubject(subject) {
            // Handle subject selection with toggle behavior
            if (this.selectedSubject && this.selectedSubject.id === subject.id) {
                this.selectedSubject = null;
                this.chapters = [];
                this.selectedChapter = null;
                this.quizzes = [];
            } else {
                this.selectedSubject = subject;
                this.fetchChapters(subject.id);
                // Reset chapter and quiz selections when changing subjects
                this.selectedChapter = null;
                this.quizzes = [];
            }
        },

        saveSubject() {
            // Save a new or edited subject
            const method = this.editingSubject ? 'put' : 'post';
            const url = this.editingSubject ? 
                `/api/subjects/${this.editingSubject.id}` : '/api/subjects';

            axios[method](url, this.subjectForm)
                .then(() => {
                    this.closeSubjectModal();
                    this.fetchSubjects();
                })
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error saving subject';
                });
        },

        editSubject(subject) {
            // Prepare subject for editing
            console.log('Editing subject:', subject);
            this.editingSubject = subject;
            this.subjectForm = { 
                name: subject.name, 
                description: subject.description 
            };
            this.showSubjectModal = true;
            document.body.classList.add('modal-open');
        },

        deleteSubject(id) {
            // Delete a subject after confirmation
            if (confirm('Are you sure you want to delete this subject?')) {
                axios.delete(`/api/subjects/${id}`)
                    .then(() => this.fetchSubjects())
                    .catch(error => {
                        this.error = error.response?.data?.message || 'Error deleting subject';
                        setTimeout(() => this.error = null, 5000);
                    });
            }
        },

        // --------------- Chapter Operations --------------- 
        fetchChapters(subjectId) {
            // Retrieve chapters for a specific subject
            axios.get(`/api/subjects/${subjectId}/chapters`)
                .then(response => this.chapters = response.data)
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error fetching chapters';
                    setTimeout(() => this.error = null, 5000);
                });
        },

        saveChapter() {
            // Save a new or edited chapter
            const method = this.editingChapter ? 'put' : 'post';
            const url = this.editingChapter ? 
                `/api/chapters/${this.editingChapter.id}` : '/api/chapters';
            
            const data = {
                ...this.chapterForm,
                subject_id: this.selectedSubject.id
            };

            axios[method](url, data)
                .then(() => {
                    this.closeChapterModal();
                    this.fetchChapters(this.selectedSubject.id);
                })
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error saving chapter';
                });
        },

        editChapter(chapter) {
            // Prepare chapter for editing
            this.editingChapter = chapter;
            this.chapterForm = { 
                name: chapter.name, 
                description: chapter.description 
            };
            this.showChapterModal = true;
            document.body.classList.add('modal-open');
        },

        deleteChapter(id) {
            // Delete a chapter after confirmation
            if (confirm('Are you sure you want to delete this chapter?')) {
                axios.delete(`/api/chapters/${id}`)
                    .then(() => this.fetchChapters(this.selectedSubject.id))
                    .catch(error => {
                        this.error = error.response?.data?.message || 'Error deleting chapter';
                        setTimeout(() => this.error = null, 5000);
                    });
            }
        },

        // --------------- Quiz Operations --------------- 
        fetchQuizzes(chapterId) {
            // Retrieve quizzes for a specific chapter
            axios.get(`/api/chapters/${chapterId}/quizzes`)
                .then(response => this.quizzes = response.data)
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error fetching quizzes';
                    setTimeout(() => this.error = null, 5000);
                });
        },

        selectChapter(chapter) {
            // Handle chapter selection with toggle behavior
            if (this.selectedChapter && this.selectedChapter.id === chapter.id) {
                this.selectedChapter = null;
                this.quizzes = [];
            } else {
                this.selectedChapter = chapter;
                this.fetchQuizzes(chapter.id);
            }
        },

        // --------------- Modal Management --------------- 
        openSubjectModal() {
            // Initialize and display subject creation/editing modal
            console.log('Opening subject modal');
            this.editingSubject = null;
            this.subjectForm = { name: '', description: '' };
            this.showSubjectModal = true;
            document.body.classList.add('modal-open');
        },

        openChapterModal() {
            // Initialize and display chapter creation/editing modal
            if (!this.selectedSubject) {
                this.error = 'Please select a subject first';
                return;
            }
            this.editingChapter = null;
            this.chapterForm = { name: '', description: '' };
            this.showChapterModal = true;
            document.body.classList.add('modal-open');
        },

        closeSubjectModal() {
            // Clean up and close subject modal
            console.log('Closing subject modal');
            this.showSubjectModal = false;
            this.editingSubject = null;
            this.subjectForm = { name: '', description: '' };
            document.body.classList.remove('modal-open');
            this.error = null;
        },

        closeChapterModal() {
            // Clean up and close chapter modal
            this.showChapterModal = false;
            this.editingChapter = null;
            this.chapterForm = { name: '', description: '' };
            document.body.classList.remove('modal-open');
            this.error = null;
        },

        // --------------- Event Handlers --------------- 
        closeModalOnEscape(e) {
            // Handle ESC key press for modal closing
            if (e.key === 'Escape') {
                if (this.showSubjectModal) this.closeSubjectModal();
                if (this.showChapterModal) this.closeChapterModal();
            }
        },

        showSection(section) {
            // Navigate to different sections
            if (section === 'users') {
                window.location.href = '/admin/user-management';
            } else if (section === 'reports') {
                window.location.href = '/admin/reports';
            }
        },

        loadChaptersForQuiz() {
            // Load chapters for quiz creation
            if (this.selectedSubjectId) {
                axios.get(`/api/subjects/${this.selectedSubjectId}/chapters`)
                    .then(response => {
                        this.chaptersForQuiz = response.data;
                        this.selectedChapterId = '';
                        this.quizzes = [];
                        this.selectedQuizId = null;
                    })
                    .catch(error => {
                        this.error = error.response?.data?.message || 'Error loading chapters';
                    });
            } else {
                this.chaptersForQuiz = [];
                this.selectedChapterId = '';
            }
        },

        loadQuizzes() {
            // Load quizzes for quiz creation
            if (this.selectedChapterId) {
                axios.get(`/api/chapters/${this.selectedChapterId}/quizzes`)
                    .then(response => {
                        this.quizzes = response.data;
                        this.selectedQuizId = null;
                    })
                    .catch(error => {
                        this.error = error.response?.data?.message || 'Error loading quizzes';
                    });
            } else {
                this.quizzes = [];
            }
        },

        // --------------- Background Tasks Methods --------------- 
        async triggerTask(type) {
            if (this.taskInProgress) return;
            
            this.taskInProgress = true;
            this.taskStatus = 'Starting task...';
            this.statusAlertClass = 'alert-info';
            this.statusIconClass = 'fa-spinner fa-spin';
            
            try {
                let endpoint;
                let taskName;
                switch (type) {
                    case 'report':
                        endpoint = '/api/admin/trigger-report';
                        taskName = 'Monthly Report';
                        break;
                    case 'backup':
                        endpoint = '/api/admin/trigger-backup';
                        taskName = 'Database Backup';
                        break;
                    case 'analytics':
                        endpoint = '/api/admin/export-analytics';
                        taskName = 'Analytics Export';
                        break;
                }
                
                const response = await axios.get(endpoint);
                if (response.data.task_id) {
                    this.taskStatus = `${taskName} task started...`;
                    this.pollTaskStatus(response.data.task_id, taskName);
                } else {
                    throw new Error('No task ID received');
                }
            } catch (error) {
                console.error('Task error:', error);
                this.handleTaskError(error);
            }
        },

        async pollTaskStatus(taskId, taskName) {
            try {
                const response = await axios.get(`/api/task-status/${taskId}`);
                const status = response.data;
                
                switch (status.state) {
                    case 'SUCCESS':
                        this.taskStatus = `${taskName} completed successfully!`;
                        this.statusAlertClass = 'alert-success';
                        this.statusIconClass = 'fa-check-circle';
                        this.taskInProgress = false;
                        break;
                    case 'FAILURE':
                        throw new Error(status.result || `${taskName} failed`);
                    case 'PENDING':
                        this.taskStatus = `${taskName} is pending...`;
                        setTimeout(() => this.pollTaskStatus(taskId, taskName), 2000);
                        break;
                    case 'STARTED':
                        this.taskStatus = `${taskName} is in progress...`;
                        setTimeout(() => this.pollTaskStatus(taskId, taskName), 2000);
                        break;
                    default:
                        setTimeout(() => this.pollTaskStatus(taskId, taskName), 2000);
                }
            } catch (error) {
                this.handleTaskError(error);
            }
        },

        handleTaskError(error) {
            console.error('Task error:', error);
            this.taskStatus = `Error: ${error.message || 'Task failed'}`;
            this.statusAlertClass = 'alert-danger';
            this.statusIconClass = 'fa-exclamation-circle';
            this.taskInProgress = false;
        },
    },
    
    // --------------- Lifecycle Hooks --------------- 
    mounted() {
        // Initialize the application
        console.log('Vue app mounted');
        this.fetchSubjects();
        document.addEventListener('keydown', this.closeModalOnEscape);
        // Make Vue instance available for debugging
        window.app = this;

        // Get currentSection from URL hash or default to 'subjects'
        this.currentSection = window.location.hash.substring(1) || 'subjects';
    },
    
    beforeDestroy() {
        // Clean up event listeners
        document.removeEventListener('keydown', this.closeModalOnEscape);
    }
});
