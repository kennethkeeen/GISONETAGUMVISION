/**
 * Real-Time Updates using Server-Sent Events (SSE)
 * Handles notifications, dashboard updates, and project status changes
 */

class RealtimeManager {
    constructor() {
        this.eventSources = {};
        this.callbacks = {
            notifications: [],
            dashboard: [],
            projects: []
        };
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    /**
     * Connect to notifications stream
     */
    connectNotifications(callback) {
        if (this.callbacks.notifications.indexOf(callback) === -1) {
            this.callbacks.notifications.push(callback);
        }

        if (this.eventSources.notifications) {
            return; // Already connected
        }

        const url = '/projeng/api/realtime/notifications/';
        this._connectSSE('notifications', url);
    }

    /**
     * Connect to dashboard updates stream
     */
    connectDashboard(callback) {
        if (this.callbacks.dashboard.indexOf(callback) === -1) {
            this.callbacks.dashboard.push(callback);
        }

        if (this.eventSources.dashboard) {
            return; // Already connected
        }

        const url = '/projeng/api/realtime/dashboard/';
        this._connectSSE('dashboard', url);
    }

    /**
     * Connect to project status stream
     */
    connectProjects(callback, projectId = null) {
        if (this.callbacks.projects.indexOf(callback) === -1) {
            this.callbacks.projects.push(callback);
        }

        const key = projectId ? `projects_${projectId}` : 'projects';
        if (this.eventSources[key]) {
            return; // Already connected
        }

        const url = projectId 
            ? `/projeng/api/realtime/projects/${projectId}/`
            : '/projeng/api/realtime/projects/';
        this._connectSSE(key, url);
    }

    /**
     * Internal method to connect SSE
     */
    _connectSSE(key, url) {
        const eventSource = new EventSource(url);
        
        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this._handleMessage(key, data);
            } catch (e) {
                console.error('Error parsing SSE data:', e);
            }
        };

        eventSource.onerror = (error) => {
            console.error(`SSE connection error for ${key}:`, error);
            this._handleError(key, error);
        };

        eventSource.onopen = () => {
            console.log(`SSE connected: ${key}`);
            this.isConnected = true;
            this.reconnectAttempts = 0;
        };

        this.eventSources[key] = eventSource;
    }

    /**
     * Handle incoming messages
     */
    _handleMessage(key, data) {
        if (data.type === 'error') {
            console.error('SSE error:', data.message);
            return;
        }

        // Route to appropriate callbacks
        if (key === 'notifications' || key.startsWith('notifications')) {
            this.callbacks.notifications.forEach(cb => cb(data));
        }
        
        if (key === 'dashboard' || key.startsWith('dashboard')) {
            this.callbacks.dashboard.forEach(cb => cb(data));
        }
        
        if (key === 'projects' || key.startsWith('projects')) {
            this.callbacks.projects.forEach(cb => cb(data));
        }
    }

    /**
     * Handle connection errors
     */
    _handleError(key, error) {
        const eventSource = this.eventSources[key];
        if (eventSource) {
            eventSource.close();
            delete this.eventSources[key];
        }

        // Attempt reconnection
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
            console.log(`Reconnecting ${key} in ${delay}ms...`);
            
            setTimeout(() => {
                // Reconnect based on key
                if (key === 'notifications') {
                    this.connectNotifications(() => {});
                } else if (key === 'dashboard') {
                    this.connectDashboard(() => {});
                } else if (key.startsWith('projects')) {
                    const projectId = key.includes('_') ? parseInt(key.split('_')[1]) : null;
                    this.connectProjects(() => {}, projectId);
                }
            }, delay);
        } else {
            console.error(`Max reconnection attempts reached for ${key}`);
            this.isConnected = false;
        }
    }

    /**
     * Disconnect all streams
     */
    disconnect() {
        Object.keys(this.eventSources).forEach(key => {
            if (this.eventSources[key]) {
                this.eventSources[key].close();
                delete this.eventSources[key];
            }
        });
        this.callbacks = {
            notifications: [],
            dashboard: [],
            projects: []
        };
        this.isConnected = false;
    }

    /**
     * Disconnect specific stream
     */
    disconnectStream(key) {
        if (this.eventSources[key]) {
            this.eventSources[key].close();
            delete this.eventSources[key];
        }
    }
}

// Global instance
window.realtimeManager = new RealtimeManager();

/**
 * Notification Handler
 */
function setupRealtimeNotifications() {
    const notificationBell = document.getElementById('notification-bell');
    const notificationCount = document.getElementById('notification-count');
    
    if (!notificationBell) return;

    window.realtimeManager.connectNotifications((data) => {
        if (data.type === 'notification') {
            // Update notification count
            if (notificationCount) {
                notificationCount.textContent = data.unread_count;
                notificationCount.classList.remove('hidden');
                
                if (data.unread_count === 0) {
                    notificationCount.classList.add('hidden');
                } else {
                    // Add animation
                    notificationCount.classList.add('animate-pulse');
                    setTimeout(() => {
                        notificationCount.classList.remove('animate-pulse');
                    }, 1000);
                }
            }

            // Show browser notification if permission granted
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('New Notification', {
                    body: data.notification.message,
                    icon: '/static/img/tagum.jpg'
                });
            }

            // Show toast notification
            showToastNotification(data.notification.message);
        }
    });
}

/**
 * Dashboard Updates Handler
 */
function setupRealtimeDashboard() {
    window.realtimeManager.connectDashboard((data) => {
        if (data.type === 'dashboard_update') {
            // Update status counts
            if (data.status_counts) {
                updateDashboardCards(data.status_counts, data.total_projects);
            }

            // Show recent updates
            if (data.recent_updates && data.recent_updates.length > 0) {
                showRecentUpdates(data.recent_updates);
            }
        }
    });
}

/**
 * Project Status Handler
 */
function setupRealtimeProjects(projectId = null) {
    window.realtimeManager.connectProjects((data) => {
        if (data.type === 'project_status') {
            if (projectId && data.project_id === projectId) {
                // Update single project
                updateProjectStatus(data);
            } else if (!projectId && data.projects) {
                // Update multiple projects
                data.projects.forEach(project => {
                    updateProjectStatus(project);
                });
            }
        }
    }, projectId);
}

/**
 * Helper: Update dashboard cards
 */
function updateDashboardCards(statusCounts, totalProjects) {
    // Update total projects - try multiple possible IDs
    const totalEl = document.getElementById('total-projects') || 
                    document.getElementById('card-total-projects') ||
                    document.querySelector('[id*="total"]');
    if (totalEl) {
        totalEl.textContent = totalProjects;
    }

    // Update status counts - try multiple possible ID patterns
    ['planned', 'in_progress', 'completed', 'delayed'].forEach(status => {
        // Try different ID patterns
        const el = document.getElementById(`status-${status}`) ||
                   document.getElementById(`card-${status}`) ||
                   document.getElementById(`card-${status.replace('_', '-')}`);
        
        if (el && statusCounts[status] !== undefined) {
            const oldValue = parseInt(el.textContent) || 0;
            const newValue = statusCounts[status];
            if (oldValue !== newValue) {
                el.textContent = newValue;
                // Add highlight animation
                el.classList.add('text-yellow-500', 'font-bold');
                setTimeout(() => {
                    el.classList.remove('text-yellow-500', 'font-bold');
                }, 2000);
            }
        }
    });
}

/**
 * Helper: Show recent updates
 */
function showRecentUpdates(updates) {
    // Create or update recent updates section
    let updatesContainer = document.getElementById('recent-updates');
    if (!updatesContainer) {
        updatesContainer = document.createElement('div');
        updatesContainer.id = 'recent-updates';
        updatesContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
        document.body.appendChild(updatesContainer);
    }

    updates.forEach(update => {
        const updateEl = document.createElement('div');
        updateEl.className = 'bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg animate-fade-in';
        updateEl.innerHTML = `
            <div class="font-semibold">${update.name}</div>
            <div class="text-sm">Status: ${update.status}</div>
        `;
        updatesContainer.appendChild(updateEl);

        // Remove after 5 seconds
        setTimeout(() => {
            updateEl.remove();
        }, 5000);
    });
}

/**
 * Helper: Update project status
 */
function updateProjectStatus(data) {
    const projectEl = document.querySelector(`[data-project-id="${data.id}"]`);
    if (projectEl) {
        // Update status badge
        const statusBadge = projectEl.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.textContent = data.status;
            statusBadge.className = `status-badge status-${data.status}`;
        }

        // Update progress if available
        if (data.progress !== undefined) {
            const progressBar = projectEl.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${data.progress}%`;
            }
        }

        // Add highlight animation
        projectEl.classList.add('bg-yellow-100');
        setTimeout(() => {
            projectEl.classList.remove('bg-yellow-100');
        }, 2000);
    }
}

/**
 * Helper: Show toast notification
 */
function showToastNotification(message) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 bg-blue-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 animate-fade-in';
    toast.innerHTML = `
        <div class="flex items-center gap-3">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(toast);

    // Remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

/**
 * Request notification permission
 */
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Request notification permission
    requestNotificationPermission();

    // Setup real-time features based on page
    const path = window.location.pathname;
    
    if (path.includes('dashboard') || path === '/') {
        setupRealtimeDashboard();
        setupRealtimeNotifications();
    } else if (path.includes('projects')) {
        const projectIdMatch = path.match(/projects\/(\d+)/);
        if (projectIdMatch) {
            setupRealtimeProjects(parseInt(projectIdMatch[1]));
        } else {
            setupRealtimeProjects();
        }
        setupRealtimeNotifications();
    } else {
        // Setup notifications on all pages
        setupRealtimeNotifications();
    }

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        window.realtimeManager.disconnect();
    });
});

