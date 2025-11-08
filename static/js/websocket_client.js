/**
 * WebSocket Client for Real-Time Updates (Phase 4: Parallel to SSE)
 * Handles notifications and project updates via WebSocket connections
 * Works alongside existing SSE system for redundancy and reliability
 */

class WebSocketManager {
    constructor() {
        this.sockets = {
            notifications: null,
            projects: null
        };
        this.callbacks = {
            notifications: [],
            dashboard: [],
            projects: []
        };
        this.reconnectAttempts = {
            notifications: 0,
            projects: 0
        };
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3 seconds
        this.isEnabled = true; // Can be toggled via feature flag
    }

    /**
     * Check if WebSocket is enabled (via feature flag or settings)
     */
    isWebSocketEnabled() {
        // Check if WebSocket is explicitly disabled
        if (window.DISABLE_WEBSOCKET === true) {
            return false;
        }
        // Check if WebSocket is explicitly enabled
        if (window.ENABLE_WEBSOCKET === true) {
            return true;
        }
        // Default: Disable WebSocket by default - SSE is primary and more reliable
        // WebSocket can be enabled via window.ENABLE_WEBSOCKET = true if needed
        return false;
    }

    /**
     * Get WebSocket URL based on current protocol
     */
    getWebSocketURL(path) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        return `${protocol}//${window.location.host}${path}`;
    }

    /**
     * Connect to notifications WebSocket
     */
    connectNotifications(callback) {
        if (!this.isWebSocketEnabled()) {
            console.log('⚠️  WebSocket disabled, using SSE only');
            return;
        }

        // Add callback
        if (this.callbacks.notifications.indexOf(callback) === -1) {
            this.callbacks.notifications.push(callback);
        }

        // Already connected
        if (this.sockets.notifications && this.sockets.notifications.readyState === WebSocket.OPEN) {
            return;
        }

        const wsUrl = this.getWebSocketURL('/ws/notifications/');
        this._connectWebSocket('notifications', wsUrl);
    }

    /**
     * Connect to project updates WebSocket
     */
    connectProjects(callback) {
        if (!this.isWebSocketEnabled()) {
            console.log('⚠️  WebSocket disabled, using SSE only');
            return;
        }

        // Add callback
        if (this.callbacks.projects.indexOf(callback) === -1) {
            this.callbacks.projects.push(callback);
        }

        // Already connected
        if (this.sockets.projects && this.sockets.projects.readyState === WebSocket.OPEN) {
            return;
        }

        const wsUrl = this.getWebSocketURL('/ws/projects/');
        this._connectWebSocket('projects', wsUrl);
    }

    /**
     * Internal method to connect WebSocket
     */
    _connectWebSocket(key, url) {
        try {
            const socket = new WebSocket(url);

            socket.onopen = () => {
                // Only log successful connection - SSE is primary, WebSocket is bonus
                console.log(`✅ WebSocket connected: ${key} (bonus feature)`);
                this.reconnectAttempts[key] = 0;
                this._notifyCallbacks(key, {
                    type: 'connection',
                    status: 'connected',
                    source: 'websocket'
                });
            };

            socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    // Silently handle messages - no console spam
                    this._handleMessage(key, data);
                } catch (e) {
                    // Only log parsing errors, not connection errors
                    console.error(`Error parsing WebSocket data for ${key}:`, e);
                }
            };

            socket.onerror = (error) => {
                // Silently handle WebSocket errors - SSE is the primary system
                // Only log on first attempt to avoid console spam
                if (this.reconnectAttempts[key] === 0) {
                    console.log(`ℹ️  WebSocket not available for ${key}, using SSE only`);
                }
                this._notifyCallbacks(key, {
                    type: 'error',
                    source: 'websocket',
                    error: error
                });
            };

            socket.onclose = (event) => {
                // Silently handle disconnections - SSE is the primary system
                this.sockets[key] = null;

                // Attempt to reconnect if not a normal closure and haven't exceeded max attempts
                if (event.code !== 1000 && this.reconnectAttempts[key] < this.maxReconnectAttempts) {
                    this.reconnectAttempts[key]++;
                    const delay = this.reconnectDelay * this.reconnectAttempts[key];
                    // Only log first reconnection attempt
                    if (this.reconnectAttempts[key] === 1) {
                        console.log(`ℹ️  WebSocket unavailable, using SSE for ${key}`);
                    }
                    setTimeout(() => {
                        this._connectWebSocket(key, url);
                    }, delay);
                } else if (this.reconnectAttempts[key] >= this.maxReconnectAttempts) {
                    // Silently fall back to SSE - no console spam
                    this._notifyCallbacks(key, {
                        type: 'connection',
                        status: 'failed',
                        source: 'websocket',
                        message: 'WebSocket connection failed. Using SSE fallback.'
                    });
                }
            };

            this.sockets[key] = socket;
        } catch (error) {
            console.error(`Failed to create WebSocket connection for ${key}:`, error);
            this._notifyCallbacks(key, {
                type: 'error',
                source: 'websocket',
                error: error
            });
        }
    }

    /**
     * Handle incoming WebSocket messages
     */
    _handleMessage(key, data) {
        // Handle different message types
        if (data.type === 'notification') {
            // Notification update
            this._notifyCallbacks('notifications', data);
        } else if (data.type === 'project_created' || data.type === 'project_updated' || 
                   data.type === 'project_deleted' || data.type === 'project_status_changed' ||
                   data.type === 'cost_updated' || data.type === 'progress_updated') {
            // Project update
            this._notifyCallbacks('projects', data);
            // Also notify dashboard callbacks for project updates
            this._notifyCallbacks('dashboard', {
                type: 'dashboard_update',
                project_update: data,
                source: 'websocket'
            });
        } else {
            // Generic message
            this._notifyCallbacks(key, data);
        }
    }

    /**
     * Notify all callbacks for a specific key
     */
    _notifyCallbacks(key, data) {
        const callbacks = this.callbacks[key] || [];
        callbacks.forEach(callback => {
            try {
                callback(data);
            } catch (e) {
                console.error(`Error in callback for ${key}:`, e);
            }
        });
    }

    /**
     * Disconnect all WebSocket connections
     */
    disconnect() {
        Object.keys(this.sockets).forEach(key => {
            if (this.sockets[key]) {
                this.sockets[key].close(1000, 'Client disconnecting');
                this.sockets[key] = null;
            }
        });
        console.log('🔌 All WebSocket connections closed');
    }

    /**
     * Get connection status
     */
    getStatus() {
        return {
            notifications: this.sockets.notifications ? this.sockets.notifications.readyState : WebSocket.CLOSED,
            projects: this.sockets.projects ? this.sockets.projects.readyState : WebSocket.CLOSED,
            enabled: this.isWebSocketEnabled()
        };
    }
}

// Global WebSocket manager instance
window.wsManager = new WebSocketManager();

// Auto-connect on page load (if WebSocket is enabled)
document.addEventListener('DOMContentLoaded', function() {
    // Only connect if WebSocket is enabled
    if (window.wsManager.isWebSocketEnabled()) {
        // Silently attempt WebSocket connection - SSE is primary system
        // Connect to notifications WebSocket
        window.wsManager.connectNotifications((data) => {
            // Handle notification updates (same as SSE handler)
            if (data.type === 'notification') {
                // Pass to existing SSE handler for UI updates
                // This ensures WebSocket messages use the same UI update logic as SSE
                if (window.realtimeManager && window.realtimeManager._handleMessage) {
                    window.realtimeManager._handleMessage('notifications', data);
                }
            }
        });

        // Connect to project updates WebSocket
        window.wsManager.connectProjects((data) => {
            // Handle project updates (same as SSE handler)
            // Pass to existing SSE handler for UI updates
            if (window.realtimeManager && window.realtimeManager._handleMessage) {
                // Route based on data type
                if (data.type === 'project_created' || data.type === 'project_updated' || 
                    data.type === 'project_deleted' || data.type === 'project_status_changed' ||
                    data.type === 'cost_updated' || data.type === 'progress_updated') {
                    window.realtimeManager._handleMessage('projects', data);
                    // Also trigger dashboard update
                    window.realtimeManager._handleMessage('dashboard', {
                        type: 'dashboard_update',
                        project_update: data,
                        source: 'websocket'
                    });
                } else {
                    window.realtimeManager._handleMessage('projects', data);
                }
            }
        });
    }
    // Silently use SSE only if WebSocket is disabled - no console log needed
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.wsManager) {
        window.wsManager.disconnect();
    }
});

