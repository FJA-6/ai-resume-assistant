from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, User, Resume, InterviewQuestion
from utils import allowed_file, extract_text_from_pdf, save_uploaded_file
from ai_service import analyze_resume, generate_interview_questions
from config import Config
import os

api = Blueprint('api', __name__)

@api.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # 验证必填字段
        if not username or not email or not password:
            return jsonify({'error': '用户名、邮箱和密码都是必填项'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已被注册'}), 400
        
        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

@api.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码都是必填项'}), 400
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': '用户名或密码错误'}), 401
        
        return jsonify({
            'message': '登录成功',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500

@api.route('/upload-resume', methods=['POST'])
def upload_resume():
    """上传简历接口"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        user_id = request.form.get('user_id', type=int)
        
        if not user_id:
            return jsonify({'error': '用户ID不能为空'}), 400
        
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '只支持PDF格式文件'}), 400
        
        # 验证用户是否存在
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 保存文件
        filename, file_path = save_uploaded_file(file, Config.UPLOAD_FOLDER)
        
        # 提取PDF文本
        try:
            content_text = extract_text_from_pdf(file_path)
        except Exception as e:
            # 如果PDF解析失败，删除已保存的文件
            os.remove(file_path)
            return jsonify({'error': f'PDF解析失败: {str(e)}'}), 400
        
        # 创建简历记录
        resume = Resume(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            content_text=content_text
        )
        
        db.session.add(resume)
        db.session.commit()
        
        return jsonify({
            'message': '简历上传成功',
            'resume': resume.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@api.route('/analyze-resume/<int:resume_id>', methods=['POST'])
def analyze_resume_endpoint(resume_id):
    """分析简历接口"""
    try:
        resume = Resume.query.get(resume_id)
        
        if not resume:
            return jsonify({'error': '简历不存在'}), 404
        
        if not resume.content_text:
            return jsonify({'error': '简历内容为空，无法分析'}), 400
        
        # 调用AI分析
        analysis_result = analyze_resume(resume.content_text)
        
        # 更新简历分析结果
        resume.analysis_result = analysis_result
        db.session.commit()
        
        return jsonify({
            'message': '分析完成',
            'analysis': analysis_result,
            'resume_id': resume_id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

@api.route('/generate-questions/<int:resume_id>', methods=['POST'])
def generate_questions_endpoint(resume_id):
    """生成面试题目接口"""
    try:
        resume = Resume.query.get(resume_id)
        
        if not resume:
            return jsonify({'error': '简历不存在'}), 404
        
        if not resume.content_text:
            return jsonify({'error': '简历内容为空，无法生成题目'}), 400
        
        # 获取请求参数
        data = request.get_json() or {}
        num_questions = data.get('num_questions', 10)
        
        # 调用AI生成题目
        questions_list = generate_interview_questions(
            resume.content_text,
            resume.analysis_result,
            num_questions
        )
        
        # 保存题目到数据库
        saved_questions = []
        for q in questions_list:
            question = InterviewQuestion(
                resume_id=resume_id,
                question=q['question'],
                answer=q.get('answer', '暂无参考答案'),
                category=q.get('category', '其他')
            )
            db.session.add(question)
            saved_questions.append(question)
        
        db.session.commit()
        
        return jsonify({
            'message': '题目生成成功',
            'questions': [q.to_dict() for q in saved_questions],
            'resume_id': resume_id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'生成题目失败: {str(e)}'}), 500

@api.route('/resumes/<int:user_id>', methods=['GET'])
def get_user_resumes(user_id):
    """获取用户的所有简历"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.created_at.desc()).all()
        
        return jsonify({
            'resumes': [resume.to_dict() for resume in resumes]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'获取简历列表失败: {str(e)}'}), 500

@api.route('/questions/<int:resume_id>', methods=['GET'])
def get_resume_questions(resume_id):
    """获取简历的所有面试题目"""
    try:
        resume = Resume.query.get(resume_id)
        if not resume:
            return jsonify({'error': '简历不存在'}), 404
        
        questions = InterviewQuestion.query.filter_by(resume_id=resume_id).order_by(InterviewQuestion.created_at.desc()).all()
        
        return jsonify({
            'questions': [q.to_dict() for q in questions]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'获取题目列表失败: {str(e)}'}), 500

