

// static/js/drone.js

// 无人机API类
class DroneAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem('token');
    }

    // 设置认证令牌
    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    // 获取请求头
    getHeaders() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.token}`
        };
    }

    // API请求基础方法
    async request(endpoint, method = 'GET', data = null) {
        const url = this.baseUrl + endpoint;
        const options = {
            method,
            headers: this.getHeaders()
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            
            // 处理未授权情况
            if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = '/';
                throw new Error('Unauthorized');
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // 无人机API方法
    async startDrone(data = {}) {
        return this.request('/drone/start', 'POST', data);
    }

    async stopDrone(data = {}) {
        return this.request('/drone/stop', 'POST', data);
    }

    async getDroneStatus() {
        return this.request('/drone/status');
    }

    async getDroneCoordinates() {
        return this.request('/drone/coordinates');
    }

    async sendDroneData(data) {
        return this.request('/drone/send_data', 'POST', data);
    }

    async getCommands() {
        return this.request('/drone/receive_commands');
    }

    async getLogs() {
        return this.request('/drone/logs');
    }

    async getBatteryStatus() {
        return this.request('/drone/battery');
    }

    async flyDrone(destination) {
        return this.request('/drone/fly', 'POST', { destination });
    }

    async arriveDestination(location) {
        return this.request('/drone/arrived', 'POST', { location });
    }

    // 数据API方法
    async getDashboardData() {
        return this.request('/api/dashboard');
    }

    async getHistoricalData(limit = 100) {
        return this.request(`/api/data?limit=${limit}`);
    }

    async getCommandHistory(limit = 50) {
        return this.request(`/api/commands?limit=${limit}`);
    }

    async getSystemLogs(limit = 100, type = null) {
        let url = `/api/logs?limit=${limit}`;
        if (type) {
            url += `&type=${type}`;
        }
        return this.request(url);
    }
}

// 导出API实例
const droneAPI = new DroneAPI();
