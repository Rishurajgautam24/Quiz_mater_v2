new Vue({
    el: '#app',
    
    // --------------- Data Management --------------- 
    data: {
        // User info
        username: '',           // Stores logged-in username
        
        // Error handling
        error: null,           // Error message storage
        
        // Content management
        subjects: [],          // List of all subjects
        chapters: [],          // List of chapters for selected subject
        
        // Filter states
        filters: {
            timePeriod: '30days',
            subjectId: '',
            chapterId: ''
        },
        
        // Statistics storage
        stats: {
            totalAttempts: 0,
            averageScore: 0,
            activeUsers: 0,
            totalQuizzes: 0
        },
        
        // Chart data
        quizActivity: [],      // Quiz activity data
        timeData: [],         // Time series data
        hasData: false,       // Flag for data availability
        
        // Chart instances
        charts: {
            performance: null,
            popularity: null
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
                    setTimeout(() => this.error = null, 5000);
                });
        },
        
        // --------------- Data Loading Methods --------------- 
        fetchSubjects() {
            axios.get('/api/subjects')
                .then(response => {
                    this.subjects = response.data;
                })
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error fetching subjects';
                    setTimeout(() => this.error = null, 5000);
                });
        },
        
        loadSubjectData() {
            if (this.filters.subjectId) {
                axios.get(`/api/subjects/${this.filters.subjectId}/chapters`)
                    .then(response => {
                        this.chapters = response.data;
                        this.filters.chapterId = '';
                        this.loadReports();
                    })
                    .catch(error => {
                        this.error = error.response?.data?.message || 'Error fetching chapters';
                        setTimeout(() => this.error = null, 5000);
                    });
            } else {
                this.chapters = [];
                this.filters.chapterId = '';
                this.loadReports();
            }
        },
        
        loadReports() {
            this.loadSummaryStats();
            this.loadQuizActivity();
            this.loadTimeData();
        },
        
        loadSummaryStats() {
            const params = this.getFilterParams();
            
            axios.get('/api/reports/summary', { params })
                .then(response => {
                    this.stats = response.data;
                })
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error loading summary statistics';
                    setTimeout(() => this.error = null, 5000);
                });
        },
        
        loadQuizActivity() {
            const params = this.getFilterParams();
            
            axios.get('/api/reports/quiz-activity', { params })
                .then(response => {
                    this.quizActivity = response.data;
                    this.createSubjectPopularityChart();
                    this.hasData = this.quizActivity.length > 0;
                })
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error loading quiz activity data';
                    setTimeout(() => this.error = null, 5000);
                });
        },
        
        loadTimeData() {
            const params = this.getFilterParams();
            
            axios.get('/api/reports/time-series', { params })
                .then(response => {
                    this.timeData = response.data;
                    this.createPerformanceChart();
                })
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error loading time series data';
                    setTimeout(() => this.error = null, 5000);
                });
        },
        
        getFilterParams() {
            const params = { 
                time_period: this.filters.timePeriod 
            };
            
            if (this.filters.subjectId) {
                params.subject_id = this.filters.subjectId;
            }
            
            if (this.filters.chapterId) {
                params.chapter_id = this.filters.chapterId;
            }
            
            return params;
        },
        
        // --------------- Chart Creation Methods --------------- 
        createPerformanceChart() {
            if (this.timeData.length === 0) {
                this.hasData = false;
                return;
            }
            
            this.hasData = true;
            const ctx = document.getElementById('quizPerformanceChart').getContext('2d');
            
            // Destroy existing chart if it exists
            if (this.charts.performance) {
                this.charts.performance.destroy();
            }
            
            const labels = this.timeData.map(item => item.date);
            const scoresData = this.timeData.map(item => item.avg_score);
            const attemptsData = this.timeData.map(item => item.attempts);
            
            this.charts.performance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Average Score (%)',
                            data: scoresData,
                            borderColor: 'rgba(75, 192, 192, 1)',
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderWidth: 2,
                            tension: 0.3,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Attempts',
                            data: attemptsData,
                            borderColor: 'rgba(153, 102, 255, 1)',
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            borderWidth: 2,
                            tension: 0.3,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Average Score (%)'
                            },
                            min: 0,
                            max: 100
                        },
                        y1: {
                            beginAtZero: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Number of Attempts'
                            },
                            grid: {
                                drawOnChartArea: false
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    }
                }
            });
        },
        
        createSubjectPopularityChart() {
            if (this.quizActivity.length === 0) {
                this.hasData = false;
                return;
            }
            
            this.hasData = true;
            const ctx = document.getElementById('subjectPopularityChart').getContext('2d');
            
            // Destroy existing chart if it exists
            if (this.charts.popularity) {
                this.charts.popularity.destroy();
            }
            
            // If a subject filter is active, show chapter data
            // Otherwise, show subject data
            let chartData;
            let chartLabels;
            
            if (this.filters.subjectId) {
                const chapterAttempts = {};
                this.quizActivity.forEach(activity => {
                    if (!chapterAttempts[activity.chapter_name]) {
                        chapterAttempts[activity.chapter_name] = 0;
                    }
                    chapterAttempts[activity.chapter_name] += activity.attempts;
                });
                
                chartLabels = Object.keys(chapterAttempts);
                chartData = Object.values(chapterAttempts);
            } else {
                const subjectAttempts = {};
                this.quizActivity.forEach(activity => {
                    if (!subjectAttempts[activity.subject_name]) {
                        subjectAttempts[activity.subject_name] = 0;
                    }
                    subjectAttempts[activity.subject_name] += activity.attempts;
                });
                
                chartLabels = Object.keys(subjectAttempts);
                chartData = Object.values(subjectAttempts);
            }
            
            // Generate unique colors for each segment
            const backgroundColors = this.generateColors(chartLabels.length);
            
            this.charts.popularity = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: chartLabels,
                    datasets: [{
                        data: chartData,
                        backgroundColor: backgroundColors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        },
        
        // Utility Functions
        generateColors(count) {
            const baseColors = [
                'rgba(255, 99, 132, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 206, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)',
                'rgba(153, 102, 255, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(199, 199, 199, 0.8)',
                'rgba(83, 102, 255, 0.8)',
                'rgba(40, 159, 64, 0.8)',
                'rgba(210, 199, 199, 0.8)'
            ];
            
            if (count <= baseColors.length) {
                return baseColors.slice(0, count);
            }
            
            // If we need more colors than available, generate them
            const colors = [...baseColors];
            for (let i = baseColors.length; i < count; i++) {
                const r = Math.floor(Math.random() * 255);
                const g = Math.floor(Math.random() * 255);
                const b = Math.floor(Math.random() * 255);
                colors.push(`rgba(${r}, ${g}, ${b}, 0.8)`);
            }
            
            return colors;
        },
        
        showSection(section) {
            if (section === 'users') {
                window.location.href = '/admin/user-management';
            } else if (section === 'dashboard') {
                window.location.href = '/admin/dashboard';
            } else if (section === 'quiz_management') {
                window.location.href = '/admin/quiz-management';
            }
        }
    },
    
    // --------------- Lifecycle Hooks --------------- 
    mounted() {
        this.username = document.querySelector('meta[name="username"]')?.content || '';
        this.fetchSubjects();
        this.loadReports();
        
        // Make Vue instance available for debugging
        window.app = this;
    }
});
