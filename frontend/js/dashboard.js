// Dashboard Functions

let currentPage = 0;
const ITEMS_PER_PAGE = 50;

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    initDashboard();
});

async function initDashboard() {
    // Display username
    const currentUser = localStorage.getItem('currentUser');
    document.getElementById('userDisplay').textContent = `Welcome, ${currentUser}!`;

    // Load tasks
    await loadTasks(0);

    // Add task form listener
    document.getElementById('taskForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await createTask();
    });

    // Edit form listener
    document.getElementById('editForm').addEventListener('submit', async (e) => {
        e.preventDefault();
    });
}

async function loadTasks(page = 0) {
    try {
        currentPage = page;
        const skip = page * ITEMS_PER_PAGE;
        const tasks = await apiCall(`/tasks?skip=${skip}&limit=${ITEMS_PER_PAGE}`, 'GET');
        displayTasks(tasks);
    } catch (error) {
        console.error('Failed to load tasks:', error);
        document.getElementById('tasksList').innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">Failed to load tasks. Please try again.</div>
            </div>
        `;
    }
}

function displayTasks(tasks) {
    const tasksList = document.getElementById('tasksList');
    
    if (!tasks || tasks.length === 0) {
        const emptyMsg = currentPage === 0 
            ? '<p>No tasks yet. Create one to get started!</p>'
            : '<p>No more tasks to load.</p>';
        tasksList.innerHTML = `
            <div class="col-12 text-center text-muted py-5">
                ${emptyMsg}
            </div>
        `;
        return;
    }

    let html = tasks.map(task => `
        <div class="col-md-6 col-lg-4">
            <div class="card task-card ${task.priority}-priority">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="card-title mb-0">${escapeHtml(task.title)}</h5>
                        <button class="btn btn-sm btn-danger" onclick="deleteTask(${task.id})">Delete</button>
                    </div>
                    
                    ${task.description ? `<p class="card-text text-muted small">${escapeHtml(task.description)}</p>` : ''}
                    
                    <div class="mb-3">
                        <span class="badge status-${task.status}">${formatStatus(task.status)}</span>
                        <span class="badge priority-${task.priority} ms-2">${capitalizeFirst(task.priority)}</span>
                    </div>

                    <small class="text-muted d-block mb-3">
                        Created: ${new Date(task.created_at).toLocaleDateString()}
                    </small>

                    <button class="btn btn-sm btn-primary w-100" onclick="openEditModal(${task.id}, '${escapeHtml(task.title)}', '${task.description || ''}', '${task.status}', '${task.priority}')">
                        Edit
                    </button>
                </div>
            </div>
        </div>
    `).join('');

    // Add pagination controls if there are tasks
    if (tasks.length > 0) {
        html += `
            <div class="col-12 mt-4">
                <nav aria-label="Page navigation">
                    <ul class="pagination justify-content-center">
                        <li class="page-item ${currentPage === 0 ? 'disabled' : ''}">
                            <button class="page-link" onclick="loadTasks(${currentPage - 1})">Previous</button>
                        </li>
                        <li class="page-item active">
                            <span class="page-link">Page ${currentPage + 1}</span>
                        </li>
                        <li class="page-item ${tasks.length < ITEMS_PER_PAGE ? 'disabled' : ''}">
                            <button class="page-link" onclick="loadTasks(${currentPage + 1})">Next</button>
                        </li>
                    </ul>
                </nav>
            </div>
        `;
    }

    tasksList.innerHTML = html;
}

async function createTask() {
    const title = document.getElementById('taskTitle').value.trim();
    const description = document.getElementById('taskDesc').value.trim();
    const priority = document.getElementById('taskPriority').value;
    const status = document.getElementById('taskStatus').value;
    const errorDiv = document.getElementById('taskError');

    try {
        errorDiv.classList.add('d-none');

        const newTask = await apiCall('/tasks', 'POST', {
            title,
            description: description || null,
            priority,
            status
        });

        // Reset form and reload tasks
        document.getElementById('taskForm').reset();
        await loadTasks();
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('d-none');
    }
}

function openEditModal(taskId, title, description, status, priority) {
    document.getElementById('editTaskId').value = taskId;
    document.getElementById('editTitle').value = title;
    document.getElementById('editDesc').value = description;
    document.getElementById('editStatus').value = status;
    document.getElementById('editPriority').value = priority;
    document.getElementById('editError').classList.add('d-none');

    const modal = new bootstrap.Modal(document.getElementById('editModal'));
    modal.show();
}

async function saveTask() {
    const taskId = document.getElementById('editTaskId').value;
    const title = document.getElementById('editTitle').value.trim();
    const description = document.getElementById('editDesc').value.trim();
    const status = document.getElementById('editStatus').value;
    const priority = document.getElementById('editPriority').value;
    const errorDiv = document.getElementById('editError');

    try {
        errorDiv.classList.add('d-none');

        await apiCall(`/tasks/${taskId}`, 'PUT', {
            title,
            description: description || null,
            status,
            priority
        });

        // Close modal and reload
        bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
        await loadTasks();
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('d-none');
    }
}

async function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        try {
            await apiCall(`/tasks/${taskId}`, 'DELETE');
            await loadTasks();
        } catch (error) {
            alert('Failed to delete task: ' + error.message);
        }
    }
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatStatus(status) {
    return status.split('_').map(word => capitalizeFirst(word)).join(' ');
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
