new Vue({
    el: '#app',
    
    // --------------- Data Management --------------- 
    data: {
        // Navigation
        currentPage: 'dashboard',     // Current active page
        pageTitle: 'Student Dashboard', // Page title
        
        // User info
        username: '',                 // Logged-in username
        
        // Performance statistics
        stats: {
            totalAttempts: 0,         // Total quiz attempts
            averageScore: 0,          // Average score across all quizzes
            recentPerformance: [],    // Recent quiz performance data
            subjectPerformance: []    // Performance by subject
        },
        
        // Error handling
        error: null                   // Error message storage
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
        fetchStats() {
            axios.get('/api/student/stats')
                .then(response => {
                    this.stats = response.data;
                })
                .catch(error => {
                    console.error('Error fetching stats:', error);
                    this.error = error.response?.data?.message || 'Error fetching statistics';
                });
        },
        
        // --------------- UI Helper Methods --------------- 
        getProgressBarClass(score) {
            if (score >= 75) return 'bg-success';
            if (score >= 40) return 'bg-warning';
            return 'bg-danger';
        }
    },
    
    // --------------- Lifecycle Hooks --------------- 
    mounted() {
        axios.get('/api/current-user')
            .then(response => {
                this.username = response.data.username;
            })
            .catch(error => console.error('Error fetching user:', error));
            
        this.fetchStats();
    }
});
