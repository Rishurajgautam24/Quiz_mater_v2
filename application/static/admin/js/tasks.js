new Vue({
    el: '#app',
    data: {
        username: '',
        error: null,
        taskInProgress: false,
        taskStatus: null,
        statusAlertClass: '',
        statusIconClass: ''
    },

    methods: {
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
                    default:
                        throw new Error('Invalid task type');
                }
                
                console.log(`Triggering task: ${taskName} at ${endpoint}`);
                const response = await axios.get(endpoint);
                console.log('Task response:', response.data);

                if (response.data && response.data.task_id) {
                    this.taskStatus = `${taskName} task started...`;
                    await this.pollTaskStatus(response.data.task_id, taskName);
                } else {
                    throw new Error(`No task ID received from ${taskName}`);
                }
            } catch (error) {
                console.error('Task error:', error);
                this.handleTaskError(error.response?.data?.error || error.message || 'Task failed to start');
            }
        },

        async pollTaskStatus(taskId, taskName) {
            try {
                console.log(`Polling status for task ${taskId}`);
                const response = await axios.get(`/api/task-status/${taskId}`);
                console.log('Poll response:', response.data);
                
                if (!response.data || !response.data.state) {
                    throw new Error('Invalid status response');
                }

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
                        await new Promise(resolve => setTimeout(resolve, 2000));
                        await this.pollTaskStatus(taskId, taskName);
                        break;
                    case 'STARTED':
                        this.taskStatus = `${taskName} is in progress...`;
                        await new Promise(resolve => setTimeout(resolve, 2000));
                        await this.pollTaskStatus(taskId, taskName);
                        break;
                    default:
                        this.taskStatus = `${taskName} status: ${status.state}`;
                        await new Promise(resolve => setTimeout(resolve, 2000));
                        await this.pollTaskStatus(taskId, taskName);
                }
            } catch (error) {
                console.error('Poll error:', error);
                this.handleTaskError(`${taskName}: ${error.response?.data?.error || error.message}`);
            }
        },

        handleTaskError(errorMessage) {
            console.error('Task failed:', errorMessage);
            this.taskStatus = `Error: ${errorMessage}`;
            this.statusAlertClass = 'alert-danger';
            this.statusIconClass = 'fa-exclamation-circle';
            this.taskInProgress = false;
        },

        logout() {
            axios.post('/api/logout')
                .then(() => window.location.href = '/')
                .catch(error => {
                    this.error = error.response?.data?.message || 'Error logging out';
                });
        }
    },

    mounted() {
        this.username = document.querySelector('meta[name="username"]')?.content || '';
    }
});
