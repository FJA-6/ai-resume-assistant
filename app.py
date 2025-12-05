from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
from config import Config
from models import db
from routes import api

def create_app():
    """创建Flask应用"""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    
    # 启用CORS，允许跨域请求
    CORS(app)
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(api, url_prefix='/api')
    
    # 前端页面路由
    @app.route('/')
    def index():
        return redirect(url_for('login'))
    
    @app.route('/login.html')
    def login():
        return render_template('login.html')
    
    @app.route('/register.html')
    def register():
        return render_template('register.html')
    
    @app.route('/dashboard.html')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/resume.html')
    def resume():
        return render_template('resume.html')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

