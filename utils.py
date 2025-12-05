import os
import PyPDF2
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """从PDF文件中提取文本"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise Exception(f"PDF解析失败: {str(e)}")

def save_uploaded_file(file, upload_folder):
    """保存上传的文件"""
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    filename = secure_filename(file.filename)
    # 添加时间戳避免文件名冲突
    import time
    timestamp = int(time.time())
    filename = f"{timestamp}_{filename}"
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    return filename, file_path

