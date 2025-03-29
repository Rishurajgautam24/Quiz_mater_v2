new Vue({
    el: '#app',
    
    // --------------- Data Management --------------- 
    data: {
        // User info
        username: '',               // Logged-in username
        
        // UI states
        loading: true,             // Loading indicator
        error: null,              // Error message storage
        
        // Statistics
        stats: {
            averageScore: 0,       // Overall average score
            totalAttempts: 0,      // Total number of attempts
            passRate: 0            // Percentage of passing scores
        },
        
        // Content management
        attempts: [],             // List of quiz attempts
        searchQuery: '',         // Search query string
        selectedAttempt: null    // Currently selected attempt
    },
    
    // --------------- Computed Properties --------------- 
    computed: {
        filteredAttempts() {
            if (!this.searchQuery) return this.attempts;
            
            const query = this.searchQuery.toLowerCase();
            return this.attempts.filter(attempt => 
                attempt.quiz_title.toLowerCase().includes(query) ||
                attempt.subject_name.toLowerCase().includes(query)
            );
        }
    },
    
    // --------------- Methods --------------- 
    methods: {
        // --------------- Formatting Methods --------------- 
        formatDate(dateString) {
            return new Date(dateString).toLocaleString();
        },
        
        // --------------- UI Helper Methods --------------- 
        getScoreColor(score) {
            if (score >= 75) return 'text-success';
            if (score >= 40) return 'text-warning';
            return 'text-danger';
        },
        
        getScoreBadgeClass(score) {
            if (score >= 75) return 'bg-success';
            if (score >= 40) return 'bg-warning';
            return 'bg-danger';
        },
        
        // --------------- Data Loading Methods --------------- 
        viewAttemptDetails(attempt) {
            this.selectedAttempt = {
                ...attempt,
                quiz_title: attempt.quiz_title,
                questions: []  // Initialize empty questions array
            };
            this.fetchAttemptDetails(attempt.id);
            const modal = new bootstrap.Modal(document.getElementById('attemptDetailsModal'));
            modal.show();
        },
        
        async fetchAttemptDetails(attemptId) {
            try {
                const response = await axios.get(`/api/student/attempts/${attemptId}`);
                
                if (response.data.error) {
                    throw new Error(response.data.error);
                }
                
                this.selectedAttempt = {
                    ...this.selectedAttempt,
                    ...response.data,
                    questions: response.data.response_sheet || []
                };
                
            } catch (error) {
                const message = error.response?.data?.error || 'Failed to load attempt details';
                alert(message);
            }
        },
        
        fetchResults() {
            this.loading = true;
            
            axios.get('/api/student/attempts')
                .then(response => {
                    if (!response.data.attempts) {
                        throw new Error('No attempts data received');
                    }
                    
                    this.attempts = response.data.attempts.map(attempt => ({
                        ...attempt,
                        score: parseFloat(attempt.score),
                        date: new Date(attempt.date)
                    }));
                    
                    this.stats = {
                        averageScore: parseFloat(response.data.stats.averageScore) || 0,
                        totalAttempts: response.data.stats.totalAttempts || 0,
                        passRate: parseFloat(response.data.stats.passRate) || 0
                    };
                })
                .catch(error => {
                    this.error = error.response?.data?.error || error.message || 'Failed to load results';
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        
        // --------------- Authentication Methods --------------- 
        logout() {
            axios.post('/api/logout')
                .then(() => window.location.href = '/')
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error logging out';
                });
        }
    },
    
    // --------------- Lifecycle Hooks --------------- 
    mounted() {
        axios.get('/api/current-user')
            .then(response => {
                this.username = response.data.username;
            })
            .catch(error => console.error('Error fetching user:', error));
            
        this.fetchResults();
    }
});
