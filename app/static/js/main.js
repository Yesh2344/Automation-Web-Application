// Main JavaScript file for the Automation Web App

// Function to update task status dynamically
function updateTaskStatus(taskId, newStatus) {
    // In a real application, this would make an AJAX call to update the task status
    console.log(`Updating task ${taskId} to status: ${newStatus}`);
    // Example AJAX call (commented out)
    /*
    fetch(`/api/tasks/${taskId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Update UI based on response
    })
    .catch((error) => {
        console.error('Error:', error);
    });
    */
}

// Function to show task progress
function showTaskProgress(taskId) {
    // This would be used to show a progress indicator for running tasks
    console.log(`Showing progress for task ${taskId}`);
}

// Initialize tooltips and popovers when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any Bootstrap components that require JavaScript
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add event listeners for task-related actions
    const taskButtons = document.querySelectorAll('.task-action-btn');
    if (taskButtons) {
        taskButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                const taskId = this.getAttribute('data-task-id');
                const action = this.getAttribute('data-action');
                
                if (action === 'view') {
                    window.location.href = `/task/${taskId}`;
                } else if (action === 'run') {
                    updateTaskStatus(taskId, 'running');
                    showTaskProgress(taskId);
                }
            });
        });
    }
});
