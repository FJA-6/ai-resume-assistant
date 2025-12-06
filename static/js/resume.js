// 简历详情页面逻辑
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

    // 获取简历ID
    const urlParams = new URLSearchParams(window.location.search);
    const resumeId = urlParams.get('id');

    if (!resumeId) {
        document.getElementById('content').innerHTML = '<div class="error-message">简历ID不存在</div>';
        return;
    }

    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('errorMessage');
    const resumeInfo = document.getElementById('resumeInfo');
    const analysisDiv = document.getElementById('analysisResult');
    const questionsDiv = document.getElementById('questionsList');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const generateBtn = document.getElementById('generateBtn');
    const numQuestionsInput = document.getElementById('numQuestions');

    let resume = null;
    let analysis = null;
    let questions = [];

    // 加载简历数据
    async function loadResumeData() {
        try {
            loadingDiv.className = 'loading';
            errorDiv.className = 'hidden';

            const response = await api.getUserResumes(user.id);
            resume = response.resumes.find(r => r.id === parseInt(resumeId));

            if (!resume) {
                throw new Error('简历不存在');
            }

            // 显示简历信息
            resumeInfo.innerHTML = `
                <p><strong>文件名：</strong>${escapeHtml(resume.filename)}</p>
                <p><strong>上传时间：</strong>${new Date(resume.created_at).toLocaleString('zh-CN')}</p>
            `;

            // 如果有分析结果，显示
            if (resume.analysis_result) {
                analysis = resume.analysis_result;
                displayAnalysis();
            }

            // 加载已有题目
            try {
                const questionsResponse = await api.getQuestions(resumeId);
                questions = questionsResponse.questions || [];
                displayQuestions();
            } catch (err) {
                console.error('加载题目失败:', err);
            }

        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.className = 'error-message';
        } finally {
            loadingDiv.className = 'hidden';
        }
    }

    // 显示分析结果
    function displayAnalysis() {
        if (analysis) {
            analysisDiv.innerHTML = `
                <div class="analysis-result">${escapeHtml(analysis).replace(/\n/g, '<br>')}</div>
            `;
            if (analyzeBtn) {
                analyzeBtn.style.display = 'none';
            }
        } else {
            analysisDiv.innerHTML = '<p style="color: #999; text-align: center; padding: 40px;">点击"开始分析"按钮，AI将为您分析简历内容</p>';
        }
    }

    // 显示题目列表
    function displayQuestions() {
        if (questions.length > 0) {
            questionsDiv.innerHTML = questions.map((q, index) => `
                <div class="question-item">
                    <span class="category">${escapeHtml(q.category || '其他')}</span>
                    <h4>题目 ${index + 1}</h4>
                    <div class="question-text">${escapeHtml(q.question)}</div>
                    ${q.answer ? `
                        <div class="answer-section">
                            <button class="btn-toggle-answer" onclick="toggleAnswer(${index})">
                                显示答案
                            </button>
                            <div class="answer-content" id="answer-${index}" style="display: none;">
                                <strong>参考答案：</strong>
                                <div class="answer-text">${escapeHtml(q.answer).replace(/\n/g, '<br>')}</div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `).join('');
        } else {
            questionsDiv.innerHTML = '<p style="color: #999; text-align: center; padding: 40px;">点击"生成题目"按钮，AI将根据您的简历生成面试题目</p>';
        }
    }

    // 分析简历
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async function() {
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = '分析中...';
            errorDiv.className = 'hidden';

            try {
                const response = await api.analyzeResume(resumeId);
                analysis = response.analysis;
                displayAnalysis();
                // 重新加载简历数据以获取最新的分析结果
                await loadResumeData();
            } catch (error) {
                errorDiv.textContent = error.message;
                errorDiv.className = 'error-message';
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = '开始分析';
            }
        });
    }

    // 生成题目
    if (generateBtn) {
        generateBtn.addEventListener('click', async function() {
            const numQuestions = parseInt(numQuestionsInput.value) || 10;
            generateBtn.disabled = true;
            generateBtn.textContent = '生成中...';
            errorDiv.className = 'hidden';

            const generatingDiv = document.getElementById('generating');
            generatingDiv.className = 'loading';

            try {
                const response = await api.generateQuestions(resumeId, numQuestions);
                questions = response.questions || [];
                displayQuestions();
            } catch (error) {
                errorDiv.textContent = error.message;
                errorDiv.className = 'error-message';
            } finally {
                generateBtn.disabled = false;
                generateBtn.textContent = '生成题目';
                generatingDiv.className = 'hidden';
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
    await loadResumeData();
    displayAnalysis();
    displayQuestions();
});

// 切换答案显示/隐藏
function toggleAnswer(index) {
    const answerDiv = document.getElementById(`answer-${index}`);
    const btn = answerDiv.previousElementSibling;
    
    if (answerDiv.style.display === 'none') {
        answerDiv.style.display = 'block';
        btn.textContent = '隐藏答案';
    } else {
        answerDiv.style.display = 'none';
        btn.textContent = '显示答案';
    }
}

// HTML转义函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

