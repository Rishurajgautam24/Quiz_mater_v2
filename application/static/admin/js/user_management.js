new Vue({
    el: '#app',
    
    // --------------- Data Management --------------- 
    data: {
        // Content management
        users: [],            // List of all users
        availableRoles: ['admin', 'stud'], // Available user roles
        
        // Modal states
        showUserModal: false,
        
        // Editing states
        editingUser: null,    // User being edited
        
        // Form data
        userForm: {
            username: '',
            email: '',
            password: '',
            roles: []
        },
        
        // Error handling
        error: null          // Error message storage
    },

    // --------------- Methods --------------- 
    methods: {
        // --------------- User Management Methods --------------- 
        fetchUsers() {
            axios.get('/api/users')
                .then(response => this.users = response.data)
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error fetching users';
                });
        },

        // --------------- Modal Management Methods --------------- 
        openUserModal() {
            this.editingUser = null;
            this.userForm = {
                username: '',
                email: '',
                password: '',
                roles: []
            };
            this.showUserModal = true;
            document.body.classList.add('modal-open');
        },

        closeUserModal() {
            this.showUserModal = false;
            this.editingUser = null;
            this.userForm = {
                username: '',
                email: '',
                password: '',
                roles: []
            };
            document.body.classList.remove('modal-open');
        },

        // --------------- User Operations --------------- 
        saveUser() {
            const method = this.editingUser ? 'put' : 'post';
            const url = this.editingUser ? 
                `/api/users/${this.editingUser.id}` : '/api/users';

            axios[method](url, this.userForm)
                .then(() => {
                    this.closeUserModal();
                    this.fetchUsers();
                })
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error saving user';
                });
        },

        editUser(user) {
            this.editingUser = user;
            this.userForm = {
                username: user.username,
                email: user.email,
                password: '',
                roles: user.roles
            };
            this.showUserModal = true;
            document.body.classList.add('modal-open');
        },

        deleteUser(id) {
            if (confirm('Are you sure you want to delete this user?')) {
                axios.delete(`/api/users/${id}`)
                    .then(() => this.fetchUsers())
                    .catch(error => {
                        this.error = error.response?.data?.message || 'Error deleting user';
                    });
            }
        },

        toggleUserStatus(user) {
            axios.patch(`/api/users/${user.id}/toggle-status`)
                .then(() => this.fetchUsers())
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error updating user status';
                });
        },

        getRoleBadgeClass(user) {
            return {
                'bg-danger': user.roles.includes('admin'),
                'bg-success': user.roles.includes('stud'),
                'bg-secondary': !user.roles.length
            };
        },

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
        this.fetchUsers();
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.showUserModal) {
                this.closeUserModal();
            }
        });
    },
    
    beforeDestroy() {
        document.removeEventListener('keydown');
    }
});
