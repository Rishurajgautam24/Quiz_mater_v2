window.initSidebar = function(username) {
    return new Vue({
        el: '#sidebar',
        data: {
            username: username
        },
        methods: {
            handleLogout() {
                axios.post('/api/logout')
                    .then(() => window.location.href = '/')
                    .catch(error => console.error('Logout failed:', error));
            }
        }
    });
};
