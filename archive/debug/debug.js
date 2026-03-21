// Debug utilities for BJJ Journal
// Add this script tag to HTML files for debugging: <script src="debug.js"></script>

class BJJDebugger {
    constructor() {
        this.enabled = localStorage.getItem('bjj_debug') === 'true';
        this.logs = [];
    }

    enable() {
        localStorage.setItem('bjj_debug', 'true');
        this.enabled = true;
        console.log('🥋 BJJ Debug mode enabled');
    }

    disable() {
        localStorage.setItem('bjj_debug', 'false');
        this.enabled = false;
        console.log('🥋 BJJ Debug mode disabled');
    }

    log(category, message, data = null) {
        if (!this.enabled) return;
        
        const timestamp = new Date().toISOString();
        const logEntry = { timestamp, category, message, data };
        this.logs.push(logEntry);
        
        console.log(`🥋 [${category}] ${message}`, data || '');
    }

    error(category, message, error = null) {
        const timestamp = new Date().toISOString();
        const logEntry = { timestamp, category, message, error: error?.message };
        this.logs.push(logEntry);
        
        console.error(`🥋 [${category}] ${message}`, error || '');
    }

    exportLogs() {
        const blob = new Blob([JSON.stringify(this.logs, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `bjj-debug-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    clearLogs() {
        this.logs = [];
        console.log('🥋 Debug logs cleared');
    }

    showStatus() {
        console.log(`🥋 Debug mode: ${this.enabled ? 'ON' : 'OFF'}`);
        console.log(`🥋 Logs collected: ${this.logs.length}`);
    }
}

// Global debug instance
window.bjjDebug = new BJJDebugger();

// Console commands
console.log('🥋 BJJ Debug utilities loaded. Commands:');
console.log('  bjjDebug.enable() - Enable debug logging');
console.log('  bjjDebug.disable() - Disable debug logging');
console.log('  bjjDebug.exportLogs() - Download debug logs');
console.log('  bjjDebug.clearLogs() - Clear debug logs');
console.log('  bjjDebug.showStatus() - Show debug status');