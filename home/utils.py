import os
from together import Together
from django.conf import settings

def APICALL(language, code):
    try:
        client = Together(api_key=settings.TOGETHER_API_KEY)
        
        #prompt shi
        prompt = f"""
        You are an expert code reviewer. Please review the following {language} code for:
        1. Syntax errors
        2. Best practices
        3. Suggestions for improvement
        
        Code to review:
        ```
        {code}
        ```
        Hint at explainations rather than explaining them encouraging learning instead of just soltuion.
        But do specify which part you are referring to.
        Do not include any thinking process or meta-commentary in your response.
        """
        
        # Make API call to Together AI
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",  # model name
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced software developer. Provide direct, code reviews without showing your thinking process. Write in proper paragraphs and do not use markdown."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.3,  
            top_p=0.9
        )
        
        
        review = response.choices[0].message.content
        #make it pretty hehe
        review = clean_ai_response(review)

        return review
        
    except Exception as e:
        # Handle API errors gracefully??
        return f"Error occurred during code review: {str(e)}"


def clean_ai_response(text):
    """
    Clean AI response by removing thinking tags and formatting properly
    """
    import re
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'</?thinking>', '', text)
    text = re.sub(r'</?analysis>', '', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  
    text = re.sub(r'^\s+|\s+$', '', text)  
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            formatted_lines.append(line)
        elif formatted_lines and formatted_lines[-1] != '':
            formatted_lines.append('') 
    
    return '\n'.join(formatted_lines)
