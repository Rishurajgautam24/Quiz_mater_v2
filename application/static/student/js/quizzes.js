new Vue({
    el: '#app',
    
    // --------------- Data Management --------------- 
    data: {
        // Navigation
        currentPage: 'quizzes',      // Current active page
        pageTitle: 'Available Quizzes', // Page title
        
        // User info
        username: '',                // Logged-in username
        
        // Loading state
        loading: true,               // Loading indicator
        
        // Content management
        quizzes: [],                // List of available quizzes
        subjects: [],               // List of subjects
        chapters: [],              // List of chapters
        
        // Filter states
        selectedSubject: '',        // Selected subject ID
        selectedChapter: '',        // Selected chapter ID
        searchQuery: '',           // Search query string
        
        // Error handling
        error: null                // Error message storage
    },
    
    // --------------- Computed Properties --------------- 
    computed: {
        filteredChapters() {
            if (!this.selectedSubject) return this.chapters;
            
            // Convert IDs to numbers for comparison
            const subjectId = Number(this.selectedSubject);
            return this.chapters.filter(c => Number(c.subject_id) === subjectId);
        },
        filteredQuizzes() {
            let filtered = this.quizzes;
            
            if (this.selectedSubject) {
                // Convert IDs to numbers for comparison
                const subjectId = Number(this.selectedSubject);
                filtered = filtered.filter(q => Number(q.subject_id) === subjectId);
            }
            
            if (this.selectedChapter) {
                // Convert IDs to numbers for comparison  
                const chapterId = Number(this.selectedChapter);
                filtered = filtered.filter(q => Number(q.chapter_id) === chapterId);
                console.log("Filtering by chapter:", chapterId, "found:", filtered.length);
            }
            
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                filtered = filtered.filter(q => 
                    q.title.toLowerCase().includes(query) ||
                    q.description.toLowerCase().includes(query) ||
                    q.subject_name.toLowerCase().includes(query) ||
                    q.chapter_name.toLowerCase().includes(query)
                );
            }
            
            return filtered;
        },
        hasActiveFilters() {
            return this.selectedSubject || this.selectedChapter || this.searchQuery;
        }
    },
    
    // --------------- Methods --------------- 
    methods: {
        // --------------- Authentication Methods --------------- 
        logout() {
            axios.post('/api/logout')
                .then(() => window.location.href = '/')
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error logging out';
                });
        },
        
        // --------------- Data Loading Methods --------------- 
        fetchCurrentUser() {
            return axios.get('/api/current-user')
                .then(response => {
                    this.username = response.data.username;
                })
                .catch(error => {
                    console.error('Error fetching user:', error);
                    this.error = 'Failed to load user data';
                });
        },
        
        fetchQuizzes() {
            this.loading = true;
            console.log("Fetching quizzes...");
            return axios.get('/api/student/available-quizzes')
                .then(response => {
                    this.quizzes = response.data;
                    console.log('Fetched quizzes:', this.quizzes.length, this.quizzes);
                })
                .catch(error => {
                    console.error('Error fetching quizzes:', error);
                    this.error = 'Failed to load quizzes';
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        
        fetchSubjects() {
            // We need to ensure this route allows student access in views.py
            return axios.get('/api/subjects')
                .then(response => {
                    this.subjects = response.data;
                    console.log('Fetched subjects:', this.subjects.length);
                })
                .catch(error => {
                    console.error('Error fetching subjects:', error);
                    this.error = 'Failed to load subjects';
                });
        },
        
        fetchChapters() {
            if (!this.selectedSubject) return Promise.resolve([]);
            
            console.log("Fetching chapters for subject:", this.selectedSubject);
            return axios.get(`/api/subjects/${this.selectedSubject}/chapters`)
                .then(response => {
                    this.chapters = response.data;
                    console.log('Fetched chapters:', this.chapters);
                    
                    // If we previously had a chapter selected but it's not valid for this subject, reset it
                    if (this.selectedChapter) {
                        const chapterExists = this.chapters.some(c => c.id == this.selectedChapter);
                        if (!chapterExists) {
                            this.selectedChapter = '';
                        }
                    }
                })
                .catch(error => {
                    console.error('Error fetching chapters:', error);
                    this.error = 'Failed to load chapters';
                });
        },
        
        // --------------- Quiz Management Methods --------------- 
        startQuiz(quizId) {
            window.location.href = `/student/quiz/${quizId}`;
        },
        
        // --------------- Filter Methods --------------- 
        filterQuizzes() {
            this.loading = true;
            
            // When subject changes, fetch chapters for that subject
            if (this.selectedSubject) {
                this.fetchChapters()
                    .finally(() => {
                        this.loading = false;
                    });
            } else {
                // If subject is cleared, also clear chapter selection
                this.selectedChapter = '';
                setTimeout(() => {
                    this.loading = false;
                }, 300);
            }
        },
        
        clearFilters() {
            this.selectedSubject = '';
            this.selectedChapter = '';
            this.searchQuery = '';
            // No need to explicitly reload as computed props will handle it
        }
    },
    
    // --------------- Lifecycle Hooks --------------- 
    mounted() {
        this.loading = true;
        
        // Fix API access in views.py for these endpoints for students
        Promise.all([
            this.fetchCurrentUser(),
            this.fetchQuizzes(),
            this.fetchSubjects() 
        ])
        .catch(error => {
            console.error('Error during initialization:', error);
            this.error = 'Failed to initialize page';
        })
        .finally(() => {
            this.loading = false;
        });
    }
});
