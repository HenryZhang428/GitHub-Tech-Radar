import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class LLMAnalyzer:
    def __init__(self):
        # Prioritize Local Ollama
        self.use_local = True
        self.local_base_url = "http://localhost:11434/v1"
        self.local_model = "llama3.2:3b"
        
        # Fallback to OpenAI if configured (though we prefer local now)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.remote_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.remote_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if self.use_local:
            logger.info(f"Using Local LLM: {self.local_model}")
            self.client = OpenAI(api_key="ollama", base_url=self.local_base_url)
            self.model = self.local_model
        elif self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.remote_base_url)
            self.model = self.remote_model
        else:
            self.client = None
            logger.warning("No LLM configuration found. AI analysis will be skipped.")

    def analyze_repo(self, name, description, language):
        """
        Analyze the repository using LLM.
        """
        if not self.client:
            return self._fallback_analysis(name, description, language)

        prompt = f"""
        You are a tech trend analyst. Analyze this GitHub repository:
        Name: {name}
        Language: {language}
        Description: {description}
        
        Provide a concise, engaging summary (in Chinese) explaining:
        1. What does it do?
        2. Why is it useful/interesting?
        3. Who is it for?
        
        Keep it under 100 words. Return ONLY the summary text.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM analysis failed for {name}: {e}")
            return self._fallback_analysis(name, description, language)

    def translate(self, text, target_language):
        """
        Translate text to target language using LLM.
        """
        if not self.client:
            return text

        prompt = f"""
        Translate the following text to {target_language}. 
        Keep the tone technical and professional. 
        Return ONLY the translated text, no explanations.
        
        Text: "{text}"
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional translator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text

    def expand_search_query(self, query):
        """
        Expand search query into GitHub-friendly English keywords.
        """
        if not self.client:
            return query

        prompt = f"""
        User wants to search for GitHub repositories with this query: "{query}".
        
        Rules:
        1. If the query is a specific product/project name (e.g., "xiaozhi", "auto-gpt", "vue"), KEEP IT AS IS. Do not translate proper nouns.
        2. If the query is a general concept (e.g., "ai assistant"), convert to relevant English technical keywords.
        3. If it's a mix (e.g., "xiaozhi ai assistant"), keep the name and add keywords.
        
        Strictly output ONLY the keywords separated by space or OR.
        
        Query: {query}
        Output:
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a smart search optimizer. Preserve proper nouns."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.1
            )
            content = response.choices[0].message.content.strip()
            # Clean up potential quotes or extra text
            content = content.replace('"', '').replace("'", "")
            if "Here are" in content or "keywords" in content:
                logger.warning(f"LLM returned verbose search query: {content}")
                return query
                
            return content
        except Exception as e:
            logger.error(f"Query expansion failed: {e}")
            return query

    def _fallback_analysis(self, name, description, language):
        """
        Fallback when LLM is not available.
        """
        desc = description if description else "暂无描述"
        lang = language if language else "未知语言"
        return f"项目 {name} ({lang}): {desc}。 (AI分析不可用)"
