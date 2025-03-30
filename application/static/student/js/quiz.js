// Setup Axios defaults
axios.defaults.headers.common['X-CSRF-TOKEN'] = document.querySelector('meta[name="csrf-token"]')?.content;
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
axios.defaults.withCredentials = true;

new Vue({
    el: '#app',
    
    // --------------- Data Management --------------- 
    data: {
        // Quiz identification
        quizId: window.location.pathname.split('/').pop(), // Current quiz ID
        quizTitle: '',                                     // Quiz title
        
        // Quiz content
        questions: [],           // List of quiz questions
        answers: {},            // Student's answers
        
        // Timer management
        timeLeft: 0,            // Remaining time in seconds
        duration: 0,            // Total quiz duration
        timer: null,            // Timer interval reference
        
        // UI states
        currentQuestionIndex: 0, // Current question being displayed
        isSubmitting: false,     // Submission in progress
        loading: true,           // Loading state
        error: null,            // Error message storage
        
        // Results
        result: {
            score: 0,           // Percentage score
            total_marks: 0,     // Total available marks
            scored_marks: 0     // Marks obtained
        },
        showResults: false       // Property to manage result visibility
    },
    
    // --------------- Methods --------------- 
    methods: {
        // --------------- Timer Methods --------------- 
        formatTime(seconds) {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        },
        
        startTimer(duration) {
            this.duration = duration;
            this.timeLeft = duration * 60;
            this.timer = setInterval(() => {
                this.timeLeft--;
                if (this.timeLeft <= 0) {
                    this.submitQuiz();
                }
            }, 1000);
        },
        
        // --------------- Navigation Methods --------------- 
        nextQuestion() {
            if (this.currentQuestionIndex < this.questions.length - 1) {
                this.currentQuestionIndex++;
            }
        },
        
        prevQuestion() {
            if (this.currentQuestionIndex > 0) {
                this.currentQuestionIndex--;
            }
        },
        
        // --------------- UI Helper Methods --------------- 
        getQuestionBtnClass(questionId, index) {
            if (this.currentQuestionIndex === index) {
                return 'btn-primary';
            } else if (this.answers[questionId]) {
                return 'btn-success';
            } else {
                return 'btn-secondary';
            }
        },
        
        // --------------- Quiz Management Methods --------------- 
        confirmSubmit() {
            // Use Bootstrap's modal to confirm submission
            const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
            confirmModal.show();
        },
        
        async submitQuiz() {
            if (this.isSubmitting) return;
            
            this.isSubmitting = true;
            clearInterval(this.timer);
            
            try {
                const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
                if (!csrfToken) {
                    throw new Error('CSRF token not found');
                }

                // Validate answers before submission
                if (Object.keys(this.answers).length === 0) {
                    throw new Error('Please answer at least one question before submitting');
                }

                const response = await axios({
                    method: 'POST',
                    url: `/api/student/quiz/${this.quizId}/submit`,
                    data: { answers: this.answers },
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': csrfToken
                    }
                });

                if (response.data.error) {
                    throw new Error(response.data.error);
                }

                this.result = response.data;
                this.showResults = true;

            } catch (error) {
                console.error('Quiz submission error:', error);
                this.error = error.response?.data?.error || error.message;
                
                if (error.response?.status === 403) {
                    // Redirect to quizzes page after 3 seconds if unauthorized
                    setTimeout(() => window.location.href = '/student/quizzes', 3000);
                }
            } finally {
                this.isSubmitting = false;
            }
        },
        
        async loadQuiz() {
            this.loading = true;
            try {
                console.log("Loading quiz with ID:", this.quizId);
                const response = await axios.get(`/api/student/quiz/${this.quizId}`);
                console.log("Quiz data:", response.data);
                
                this.quizTitle = response.data.title;
                this.questions = response.data.questions;
                
                // Initialize timer only if we have questions
                if (this.questions && this.questions.length > 0) {
                    this.startTimer(response.data.duration);
                }
                
                this.error = null;
            } catch (error) {
                console.error('Error loading quiz:', error);
                this.error = 'Failed to load quiz. Please check your connection or try again later.';
            } finally {
                this.loading = false;
            }
        }
    },
    
    // --------------- Lifecycle Hooks --------------- 
    mounted() {
        console.log("Quiz page loaded, initializing Vue app");
        this.loadQuiz();
    },
    
    beforeDestroy() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }
});
