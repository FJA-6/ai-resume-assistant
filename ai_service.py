import dashscope
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
        
        response = Generation.call(
            model=Config.DASHSCOPE_CHAT_MODEL,
            messages=messages,
            result_format='message'
        )
        
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            raise Exception(f"API调用失败: {response.message}")
    
    except Exception as e:
        raise Exception(f"简历分析失败: {str(e)}")

def generate_interview_questions(resume_text, analysis_result=None, num_questions=10):
    """
    根据简历生成面试题目
    """
    if analysis_result:
        prompt = f"""基于以下简历内容和分析结果，生成{num_questions}道面试题目。
题目应该涵盖：
1. 技术技能相关问题
2. 项目经验相关问题
3. 基础知识问题
4. 行为面试问题
5. 场景题

请为每道题目标注类别（技术/项目/基础/行为/场景）。

简历内容：
{resume_text}

简历分析：
{analysis_result}

请以以下格式输出：
题目1 [类别]: 问题内容
题目2 [类别]: 问题内容
..."""
    else:
        prompt = f"""基于以下简历内容，生成{num_questions}道面试题目。
题目应该涵盖：
1. 技术技能相关问题
2. 项目经验相关问题
3. 基础知识问题
4. 行为面试问题
5. 场景题

请为每道题目标注类别（技术/项目/基础/行为/场景）。

简历内容：
{resume_text}

请以以下格式输出：
题目1 [类别]: 问题内容
题目2 [类别]: 问题内容
..."""

    try:
        messages = [
            {'role': 'system', 'content': '你是一个专业的面试官，擅长根据候选人的简历生成有针对性的面试题目。'},
            {'role': 'user', 'content': prompt}
        ]
        
        response = Generation.call(
            model=Config.DASHSCOPE_CHAT_MODEL,
            messages=messages,
            result_format='message'
        )
        
        if response.status_code == 200:
            questions_text = response.output.choices[0].message.content
            # 解析题目
            questions = parse_questions(questions_text)
            return questions
        else:
            raise Exception(f"API调用失败: {response.message}")
    
    except Exception as e:
        raise Exception(f"生成面试题目失败: {str(e)}")

def parse_questions(questions_text):
    """
    解析AI返回的题目文本，提取题目和类别
    返回格式: [{'question': '...', 'category': '...'}, ...]
    """
    questions = []
    lines = questions_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or not (line.startswith('题目') or '[' in line):
            continue
        
        # 尝试提取类别和问题
        if '[' in line and ']' in line:
            try:
                # 格式: 题目1 [类别]: 问题内容
                parts = line.split(']', 1)
                if len(parts) == 2:
                    category_part = parts[0]
                    question_part = parts[1].strip()
                    
                    # 提取类别
                    if '[' in category_part:
                        category = category_part.split('[')[1].strip()
                    else:
                        category = '其他'
                    
                    # 清理问题文本（移除"题目X:"等前缀）
                    if ':' in question_part:
                        question = question_part.split(':', 1)[1].strip()
                    else:
                        question = question_part
                    
                    if question:
                        questions.append({
                            'question': question,
                            'category': category
                        })
            except:
                # 如果解析失败，将整行作为问题
                if ':' in line:
                    question = line.split(':', 1)[1].strip()
                    if question:
                        questions.append({
                            'question': question,
                            'category': '其他'
                        })
        else:
            # 没有类别标记，直接提取问题
            if ':' in line:
                question = line.split(':', 1)[1].strip()
                if question:
                    questions.append({
                        'question': question,
                        'category': '其他'
                    })
    
    return questions

