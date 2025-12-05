// 仪表板页面逻辑
document.addEventListener('DOMContentLoaded', async function() {
    // 检查登录状态
    const user = userManager.getUser();
    if (!user) {
        window.location.href = '/login.html';
        return;
    }

    // 显示用户信息
    const userInfo = document.getElementById('userInfo');
    if (userInfo) {
        userInfo.textContent = `欢迎，${user.username}`;
    }

    const resumeList = document.getElementById('resumeList');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('errorMessage');
    const uploadErrorDiv = document.getElementById('uploadErrorMessage');
    const uploadSuccessDiv = document.getElementById('uploadSuccessMessage');
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');

    // 加载简历列表
    async function loadResumes() {
        try {
            loadingDiv.className = 'loading';
            errorDiv.className = 'hidden';
            const response = await api.getUserResumes(user.id);
            displayResumes(response.resumes || []);
        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.className = 'error-message';
        } finally {
            loadingDiv.className = 'hidden';
        }
    }

    // 显示简历列表
    function displayResumes(resumes) {
        if (resumes.length === 0) {
            resumeList.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">还没有上传简历，请先上传一份PDF简历</p>';
            return;
        }

        resumeList.innerHTML = resumes.map(resume => `
            <div class="resume-item">
                <h3>${escapeHtml(resume.filename)}</h3>
                <p><strong>上传时间：</strong>${new Date(resume.created_at).toLocaleString('zh-CN')}</p>
                ${resume.content_text ? `<p style="font-size: 14px; color: #666;">${escapeHtml(resume.content_text.substring(0, 200))}...</p>` : ''}
                <div class="resume-actions">
                    <a href="/resume.html?id=${resume.id}" class="btn btn-primary">查看详情</a>
                </div>
            </div>
        `).join('');
    }

    // 文件上传处理
    async function handleFileUpload(file) {
        if (file.type !== 'application/pdf') {
            uploadErrorDiv.textContent = '只支持PDF格式文件';
            uploadErrorDiv.className = 'error-message';
            return;
        }

        if (file.size > 16 * 1024 * 1024) {
            uploadErrorDiv.textContent = '文件大小不能超过16MB';
            uploadErrorDiv.className = 'error-message';
            return;
        }

        uploadErrorDiv.className = 'hidden';
        uploadSuccessDiv.className = 'hidden';
        const uploadingDiv = document.getElementById('uploading');
        uploadingDiv.className = 'loading';

        try {
            await api.uploadResume(file, user.id);
            uploadSuccessDiv.textContent = '简历上传成功！';
            uploadSuccessDiv.className = 'success-message';
            setTimeout(() => {
                uploadSuccessDiv.className = 'hidden';
                loadResumes();
            }, 2000);
        } catch (error) {
            uploadErrorDiv.textContent = error.message;
            uploadErrorDiv.className = 'error-message';
        } finally {
            uploadingDiv.className = 'hidden';
            fileInput.value = '';
        }
    }

    // 点击上传区域
    if (uploadArea) {
        uploadArea.addEventListener('click', () => fileInput.click());
    }

    // 文件选择
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                handleFileUpload(file);
            }
        });
    }

    // 拖拽上传
    if (uploadArea) {
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file) {
                handleFileUpload(file);
            }
        });
    }

    // 退出登录
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            userManager.clearUser();
            window.location.href = '/login.html';
        });
    }

    // 初始加载
    await loadResumes();
});

// HTML转义函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

