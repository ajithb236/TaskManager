// Admin Dashboard Functions

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    initAdminDashboard();
});

async function initAdminDashboard() {
    const currentUser = localStorage.getItem('currentUser');
    const userRole = localStorage.getItem('userRole');
    
    // Check if user is admin
    if (userRole !== 'admin') {
        document.getElementById('accessDenied').classList.remove('d-none');
        document.getElementById('statsContainer').classList.add('d-none');
        return;
    }
    
    document.getElementById('userDisplay').textContent = `Admin: ${currentUser}`;

    await loadAdminStats();
}

async function loadAdminStats() {
    try {
        const stats = await apiCall('/tasks/admin/stats', 'GET');
        
        if (!stats) {
            return;
        }

        document.getElementById('totalUsers').textContent = stats.total_users || 0;
        document.getElementById('totalTasks').textContent = stats.total_tasks || 0;
        document.getElementById('completedTasks').textContent = stats.completed_tasks || 0;

        const total = stats.total_tasks || 1;
        const completed = stats.completed_tasks || 0;
        const rate = Math.round((completed / total) * 100);
        
        const rateElement = document.getElementById('completionRate');
        rateElement.style.width = rate + '%';
        rateElement.textContent = rate + '%';
    } catch (error) {
        document.getElementById('accessDenied').classList.remove('d-none');
        document.getElementById('statsContainer').classList.add('d-none');
    }
}
