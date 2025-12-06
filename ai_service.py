import dashscope
import time
from dashscope import Generation
from config import Config

# 设置API Key
dashscope.api_key = Config.DASHSCOPE_API_KEY

def analyze_resume(resume_text):
    """
    分析简历内容
    返回分析结果
    """
    prompt = f"""请对以下简历内容进行详细分析，包括：
1. 个人信息总结
2. 教育背景分析
3. 工作经历/项目经验总结
4. 技能评估
5. 优势与亮点
6. 可能的改进建议

简历内容：
{resume_text}

请以结构化的方式输出分析结果。"""

    try:
        messages = [
            {'role': 'system', 'content': '你是一个专业的简历分析专家，擅长分析求职者的简历并提供专业的建议。'},
            {'role': 'user', 'content': prompt}
        ]
        
        response = call_api_with_retry(messages)
        return response
    
    except Exception as e:
        raise Exception(f"简历分析失败: {str(e)}")

def generate_interview_questions(resume_text, analysis_result=None, num_questions=10):
    """
    根据简历生成面试题目和参考答案
    """
    if analysis_result:
        prompt = f"""基于以下简历内容和分析结果，生成{num_questions}道面试题目，并为每道题目提供详细的参考答案。

题目应该涵盖：
1. 技术技能相关问题
2. 项目经验相关问题
3. 基础知识问题
4. 行为面试问题
5. 场景题

简历内容：
{resume_text}

简历分析：
{analysis_result}

请严格按照以下JSON格式输出，不要添加其他内容：
[
  {{"question": "问题内容", "category": "技术", "answer": "详细的参考答案"}},
  {{"question": "问题内容", "category": "项目", "answer": "详细的参考答案"}}
]"""
    else:
        prompt = f"""基于以下简历内容，生成{num_questions}道面试题目，并为每道题目提供详细的参考答案。

题目应该涵盖：
1. 技术技能相关问题
2. 项目经验相关问题
3. 基础知识问题
4. 行为面试问题
5. 场景题

简历内容：
{resume_text}

请严格按照以下JSON格式输出，不要添加其他内容：
[
  {{"question": "问题内容", "category": "技术", "answer": "详细的参考答案"}},
  {{"question": "问题内容", "category": "项目", "answer": "详细的参考答案"}}
]"""

    try:
        messages = [
            {'role': 'system', 'content': '你是一个专业的面试官，擅长根据候选人的简历生成有针对性的面试题目，并提供专业的参考答案。请严格按照JSON格式输出。'},
            {'role': 'user', 'content': prompt}
        ]
        
        response_text = call_api_with_retry(messages)
        # 解析JSON格式的题目
        questions = parse_questions_json(response_text)
        return questions
    
    except Exception as e:
        raise Exception(f"生成面试题目失败: {str(e)}")

def call_api_with_retry(messages, max_retries=3):
    """
    调用API，带重试机制
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            response = Generation.call(
                model=Config.DASHSCOPE_CHAT_MODEL,
                messages=messages,
                result_format='message',
                timeout=120  # 增加超时时间
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                last_error = f"API调用失败: {response.message}"
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                time.sleep(2)  # 重试前等待2秒
                continue
    
    raise Exception(last_error)

def parse_questions_json(response_text):
    """
    解析JSON格式的题目
    """
    import json
    import re
    
    try:
        # 尝试提取JSON数组
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            json_str = json_match.group()
            questions = json.loads(json_str)
            # 确保每个问题都有必要的字段
            result = []
            for q in questions:
                result.append({
                    'question': q.get('question', ''),
                    'category': q.get('category', '其他'),
                    'answer': q.get('answer', '暂无参考答案')
                })
            return result
    except json.JSONDecodeError:
        pass
    
    # 如果JSON解析失败，使用文本解析
    return parse_questions_text(response_text)

def parse_questions_text(questions_text):
    """
    解析文本格式的题目（备用方案）
    """
    questions = []
    
    # 按空行分割
    blocks = questions_text.strip().split('\n\n')
    
    for block in blocks:
        lines = block.strip().split('\n')
        if not lines:
            continue
        
        question = None
        category = '其他'
        answer_lines = []
        is_answer_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是答案行
            if line.startswith('答案:') or line.startswith('答案：') or line.lower().startswith('answer:'):
                is_answer_section = True
                sep = ':' if ':' in line else '：'
                answer_content = line.split(sep, 1)[1].strip() if sep in line else ''
                if answer_content:
                    answer_lines.append(answer_content)
                continue
            
            if is_answer_section:
                answer_lines.append(line)
                continue
            
            # 解析题目行
            if '题目' in line or '[' in line or line[0].isdigit():
                if '[' in line and ']' in line:
                    try:
                        parts = line.split(']', 1)
                        if len(parts) == 2:
                            category_part = parts[0]
                            question_part = parts[1].strip()
                            
                            if '[' in category_part:
                                category = category_part.split('[')[1].strip()
                            
                            if ':' in question_part or '：' in question_part:
                                sep = ':' if ':' in question_part else '：'
                                question = question_part.split(sep, 1)[1].strip()
                            else:
                                question = question_part
                    except:
                        pass
                
                if not question and (':' in line or '：' in line):
                    sep = ':' if ':' in line else '：'
                    question = line.split(sep, 1)[1].strip()
        
        answer = '\n'.join(answer_lines) if answer_lines else '暂无参考答案'
        
        if question:
            questions.append({
                'question': question,
                'category': category,
                'answer': answer
            })
    
    return questions
