import os
from together import Together
from django.conf import settings

def APICALL(language, code):
    try:
        client = Together(api_key=settings.TOGETHER_API_KEY)
        
        #prompt shi
        prompt = f"""
        You are an expert code reviewer with extensive experience in software development and best practices. 
        Please conduct a thorough review of the following {language} code.

        Review Focus Areas:
        1. Syntax errors - Identify any grammatical or structural issues that would prevent compilation or execution
        2. Best practices - Evaluate adherence to industry standards and conventional coding patterns for {language}
        3. Suggestions for improvement** - Recommend enhancements for readability, performance, maintainability, and code quality

        **Code to review:**
        ```
        {code}
        ```
        Review Guidelines:
        - Reference specific code sections by line numbers or code snippets when providing feedback
        - Hint at explanations rather than providing complete solutions - guide the developer toward understanding the underlying principles
        - Encourage learning by asking thought-provoking questions or suggesting research directions
        - Be specific about which exact part of the code each comment addresses
        - Focus on actionable feedback that the developer can implement

        Response Format:
        - Provide direct, focused feedback without meta-commentary or thinking processes
        - Structure your review clearly with distinct sections for each type of issue found
        - Use code references (e.g., "In line 15..." or "The function `calculateTotal()`...") to pinpoint exact locations

        Please begin your review now.
        """
        
        # API CALL
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",  # model name
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced software developer. Provide direct, code reviews without showing your thinking process. Write in proper paragraphs and do not use '**' for formatting."
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
