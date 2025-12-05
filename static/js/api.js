const API_BASE_URL = '/api';

// API调用函数
const api = {
    // 用户相关API
    async register(username, email, password) {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || '注册失败');
        }
        return data;
    },

    async login(username, password) {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || '登录失败');
        }
        return data;
    },

    // 简历相关API
    async uploadResume(file, userId) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', userId);

        const response = await fetch(`${API_BASE_URL}/upload-resume`, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || '上传失败');
        }
        return data;
    },

    async getUserResumes(userId) {
        const response = await fetch(`${API_BASE_URL}/resumes/${userId}`);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || '获取简历列表失败');
        }
        return data;
    },

    async analyzeResume(resumeId) {
        const response = await fetch(`${API_BASE_URL}/analyze-resume/${resumeId}`, {
            method: 'POST',
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || '分析失败');
        }
        return data;
    },

    async generateQuestions(resumeId, numQuestions = 10) {
        const response = await fetch(`${API_BASE_URL}/generate-questions/${resumeId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ num_questions: numQuestions }),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || '生成题目失败');
        }
        return data;
    },

    async getQuestions(resumeId) {
        const response = await fetch(`${API_BASE_URL}/questions/${resumeId}`);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || '获取题目失败');
        }
        return data;
    },
};

// 用户管理
const userManager = {
    getUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    },

    setUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    },

    clearUser() {
        localStorage.removeItem('user');
    },

    isLoggedIn() {
        return this.getUser() !== null;
    },
};

