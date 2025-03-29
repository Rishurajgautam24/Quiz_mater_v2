new Vue({
    el: '#app',
    
    // --------------- Data Management --------------- 
    data: {
        // App info
        message: 'Welcome to Flask + Vue App',  // Welcome message
        
        // Authentication state
        isAuthenticated: false,                 // Login status
        isLoading: false,                      // Loading state for API calls
        
        // Form data
        email: '',                             // User email input
        password: '',                          // User password input
        showPassword: false,                   // Password visibility toggle
        
        // User info
        username: '',                          // Logged in username
        
        // Error handling
        error: ''                             // Error message storage
    },
    
    // --------------- Methods --------------- 
    methods: {
        // --------------- Authentication Methods --------------- 
        login() {
            // Reset error state and show loading
            this.error = '';
            this.isLoading = true;
            
            // Attempt login with provided credentials
            axios.post('/api/login', {
                email: this.email,
                password: this.password
            })
            .then(response => {
                // Redirect based on user role
                if (response.data.role === 'admin') {
                    window.location.href = '/admin/dashboard';
                } else if (response.data.role === 'stud') {
                    window.location.href = '/student/dashboard';
                }
            })
            .catch(error => {
                console.error(error);
                this.error = error.response?.data?.message || 'Login failed';
            })
            .finally(() => {
                this.isLoading = false;
            });
        },

        logout() {
            // Clear authentication state
            this.isAuthenticated = false;
            this.username = '';
        }
    }
});
