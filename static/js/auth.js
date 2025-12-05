// 登录页面逻辑
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorDiv = document.getElementById('errorMessage');

    if (loginForm) {
        // 检查是否已登录
        if (userManager.isLoggedIn()) {
            window.location.href = '/dashboard.html';
            return;
        }

        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            errorDiv.textContent = '';
            errorDiv.className = 'hidden';

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await api.login(username, password);
                userManager.setUser(response.user);
                window.location.href = '/dashboard.html';
            } catch (error) {
                errorDiv.textContent = error.message;
                errorDiv.className = 'error-message';
            }
        });
    }

    // 注册页面逻辑
    const registerForm = document.getElementById('registerForm');
    const registerErrorDiv = document.getElementById('registerErrorMessage');
    const registerSuccessDiv = document.getElementById('registerSuccessMessage');

    if (registerForm) {
        // 检查是否已登录
        if (userManager.isLoggedIn()) {
            window.location.href = '/dashboard.html';
            return;
        }

        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            registerErrorDiv.textContent = '';
            registerErrorDiv.className = 'hidden';
            registerSuccessDiv.textContent = '';
            registerSuccessDiv.className = 'hidden';

            const username = document.getElementById('regUsername').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            const confirmPassword = document.getElementById('regConfirmPassword').value;

            if (password !== confirmPassword) {
                registerErrorDiv.textContent = '两次输入的密码不一致';
                registerErrorDiv.className = 'error-message';
                return;
            }

            if (password.length < 6) {
                registerErrorDiv.textContent = '密码长度至少为6位';
                registerErrorDiv.className = 'error-message';
                return;
            }

            try {
                await api.register(username, email, password);
                registerSuccessDiv.textContent = '注册成功！正在跳转到登录页面...';
                registerSuccessDiv.className = 'success-message';
                setTimeout(() => {
                    window.location.href = '/login.html';
                }, 1500);
            } catch (error) {
                registerErrorDiv.textContent = error.message;
                registerErrorDiv.className = 'error-message';
            }
        });
    }
});

