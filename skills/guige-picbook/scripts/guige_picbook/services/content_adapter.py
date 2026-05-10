"""内容适配服务 - 将知识内容转化为适合儿童阅读的形式"""

from ..prompts import render_prompt
from ..utils.config import Language, LLMProvider, Settings


class ContentAdapterService:
    """内容适配服务

    负责将搜索到的知识内容转化为适合目标年龄段儿童阅读的形式。
    主要功能:
    - 简化语言复杂度
    - 添加趣味性元素
    - 结构化内容
    - 生成配图描述

    支持的LLM提供商:
    - Anthropic (Claude)
    - OpenAI (ChatGPT)
    - Google (Gemini)
    - xAI (Grok)
    """

    # 语言名称映射
    LANGUAGE_NAMES = {
        Language.CHINESE: "简体中文 (Simplified Chinese)",
        Language.ENGLISH: "English",
        Language.JAPANESE: "日本語",
        Language.KOREAN: "한국어",
    }

    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = settings.default_llm_provider
        self._client = None

    def _get_language_name(self, language: Language) -> str:
        """获取语言的显示名称"""
        return self.LANGUAGE_NAMES.get(language, "English")

    def _get_client(self):
        """延迟初始化LLM客户端"""
        if self._client is not None:
            return self._client

        if self.provider == LLMProvider.ANTHROPIC:
            from anthropic import AsyncAnthropic

            self._client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)

        elif self.provider == LLMProvider.OPENAI:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
            )

        elif self.provider == LLMProvider.GEMINI:
            import google.generativeai as genai

            genai.configure(api_key=self.settings.google_api_key)
            self._client = genai.GenerativeModel(self.settings.gemini_model)

        elif self.provider == LLMProvider.GROK:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(
                api_key=self.settings.grok_api_key,
                base_url=self.settings.xai_base_url,
            )

        else:
            raise ValueError(f"不支持的LLM提供商: {self.provider}")

        return self._client

    async def _call_llm(self, prompt: str) -> str:
        """调用LLM生成内容"""
        client = self._get_client()

        if self.provider == LLMProvider.ANTHROPIC:
            response = await client.messages.create(
                model=self.settings.anthropic_model,
                max_tokens=self.settings.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        elif self.provider in (LLMProvider.OPENAI, LLMProvider.GROK):
            model = (
                self.settings.openai_model
                if self.provider == LLMProvider.OPENAI
                else self.settings.grok_model
            )
            response = await client.chat.completions.create(
                model=model,
                max_completion_tokens=self.settings.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content

        elif self.provider == LLMProvider.GEMINI:
            # Gemini SDK 是同步的，需要在异步环境中运行
            import asyncio

            response = await asyncio.to_thread(
                client.generate_content,
                prompt,
                generation_config={"max_output_tokens": self.settings.max_tokens},
            )
            return response.text

        raise ValueError(f"不支持的LLM提供商: {self.provider}")

    async def adapt(
        self,
        knowledge: dict,
        age_range: tuple[int, int],
        language: Language,
    ) -> dict:
        """将知识适配为儿童可读内容

        Args:
            knowledge: 原始知识内容
            age_range: 目标年龄范围
            language: 目标语言

        Returns:
            适配后的内容
        """
        topic = knowledge.get("topic", "")
        raw_content = "\n\n".join(knowledge.get("content", []))

        if not raw_content:
            # 如果没有搜索到内容，使用LLM直接生成
            return await self._generate_content_from_scratch(topic, age_range, language)

        # 使用LLM适配内容
        prompt = self._build_adaptation_prompt(topic, raw_content, age_range, language)
        adapted_text = await self._call_llm(prompt)

        return {
            "summary": adapted_text,
            "sources": knowledge.get("sources", []),
            "original_content": raw_content,
        }

    async def _generate_content_from_scratch(
        self,
        topic: str,
        age_range: tuple[int, int],
        language: Language,
    ) -> dict:
        """从零开始生成内容"""
        prompt = render_prompt(
            "generate_from_scratch",
            topic=topic,
            min_age=age_range[0],
            max_age=age_range[1],
            language_name=self._get_language_name(language),
        )

        adapted_text = await self._call_llm(prompt)

        return {
            "summary": adapted_text,
            "sources": ["AI generated content"],
            "original_content": "",
        }

    def _build_adaptation_prompt(
        self,
        topic: str,
        raw_content: str,
        age_range: tuple[int, int],
        language: Language,
    ) -> str:
        """构建内容适配提示词"""
        return render_prompt(
            "adapt_content",
            topic=topic,
            raw_content=raw_content,
            min_age=age_range[0],
            max_age=age_range[1],
            language_name=self._get_language_name(language),
        )

    async def generate_social_captions(
        self,
        topic: str,
        book_title: str,
        summary: str,
        language: Language,
    ) -> dict[str, str]:
        """生成双语社交媒体文案（中文 + 英文）

        Args:
            topic: 绘本主题
            book_title: 绘本标题
            summary: 绘本简介
            language: 绘本原始语言

        Returns:
            {"zh": 中文文案, "en": 英文文案}
        """
        prompt = (
            f"You are a social media copywriter for children's educational content.\n\n"
            f"A picture book has been created:\n"
            f"- Topic: {topic}\n"
            f"- Title: {book_title}\n"
            f"- Summary: {summary}\n\n"
            f"Generate TWO social media captions for parents/educators:\n\n"
            f"1. A Chinese (简体中文) caption: 2-3 sentences, warm and inviting, "
            f"highlight what children will learn.\n"
            f"2. An English caption: 2-3 sentences, engaging and educational.\n\n"
            f"Output strictly in this JSON format (no other content):\n"
            f'{{"zh": "中文文案内容", "en": "English caption content"}}'
        )
        response = await self._call_llm(prompt)

        import json

        try:
            start = response.find("{")
            end = response.rfind("}")
            if start != -1 and end != -1:
                result = json.loads(response[start : end + 1])
                return {
                    "zh": result.get("zh", f"一本关于{topic}的儿童科普绘本，适合7-10岁阅读。"),
                    "en": result.get(
                        "en",
                        f"A fun picture book about {topic} for kids ages 7-10.",
                    ),
                }
        except json.JSONDecodeError:
            pass

        return {
            "zh": f"一本关于{topic}的儿童科普绘本，适合7-10岁阅读。",
            "en": f"A fun picture book about {topic} for kids ages 7-10.",
        }

    async def generate_book_structure(
        self,
        topic: str,
        language: Language,
        age_range: tuple[int, int],
        chapter_count: int,
        adapted_content: str,
    ) -> dict:
        """生成绘本结构（标题、简介、章节大纲）

        一次LLM调用生成完整的绘本框架

        Args:
            topic: 主题
            language: 目标语言
            age_range: 目标年龄范围
            chapter_count: 章节数量
            adapted_content: 适配后的知识内容

        Returns:
            包含 title, summary, chapters 的字典
        """
        prompt = render_prompt(
            "book_structure",
            topic=topic,
            min_age=age_range[0],
            max_age=age_range[1],
            language_name=self._get_language_name(language),
            chapter_count=chapter_count,
            adapted_content=adapted_content[:2000],
        )
        response = await self._call_llm(prompt)

        # 解析JSON响应
        import json

        try:
            start = response.find("{")
            end = response.rfind("}")
            if start != -1 and end != -1:
                result = json.loads(response[start : end + 1])
                # 确保章节数量正确
                chapters = result.get("chapters", [])
                if len(chapters) < chapter_count:
                    chapters.extend([f"第{i+1}章" for i in range(len(chapters), chapter_count)])
                return {
                    "title": result.get("title", f"探索{topic}的奇妙世界"),
                    "summary": result.get("summary", ""),
                    "chapters": chapters[:chapter_count],
                }
        except json.JSONDecodeError:
            pass

        # 解析失败时返回默认值
        return {
            "title": f"探索{topic}的奇妙世界",
            "summary": f"一本为{age_range[0]}-{age_range[1]}岁儿童准备的关于{topic}的趣味绘本。",
            "chapters": [f"第{i+1}章" for i in range(chapter_count)],
        }

    async def generate_all_chapters(
        self,
        topic: str,
        chapter_titles: list[str],
        language: Language,
        age_range: tuple[int, int],
        adapted_content: str,
        include_illustration: bool = True,
    ) -> list[dict]:
        """一次性生成所有章节内容

        一次LLM调用生成所有章节的详细内容

        Args:
            topic: 绘本主题
            chapter_titles: 章节标题列表
            language: 目标语言
            age_range: 目标年龄范围
            adapted_content: 适配后的知识内容
            include_illustration: 是否生成插图描述

        Returns:
            章节内容列表
        """
        chapter_count = len(chapter_titles)
        chapters_str = "\n".join([f"{i+1}. {title}" for i, title in enumerate(chapter_titles)])

        illustration_field = ""
        illustration_instruction = ""
        if include_illustration:
            illustration_field = ',\n            "illustration_prompt": "English illustration description, 50-100 words"'
            illustration_instruction = "\n5. Provide English illustration descriptions for each chapter, suitable for AI image generation, including scene, characters, style, etc."

        prompt = render_prompt(
            "all_chapters",
            topic=topic,
            min_age=age_range[0],
            max_age=age_range[1],
            language_name=self._get_language_name(language),
            chapters_str=chapters_str,
            adapted_content=adapted_content[:2500],
            illustration_instruction=illustration_instruction,
            illustration_field=illustration_field,
        )
        response = await self._call_llm(prompt)

        # 解析JSON响应
        import json

        # 尝试匹配完整的JSON对象（包含嵌套）
        try:
            # 找到第一个 { 和最后一个 }
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                json_str = response[start:end + 1]
                result = json.loads(json_str)
                chapters = result.get("chapters", [])

                # 确保返回正确数量的章节
                parsed_chapters = []
                for i in range(chapter_count):
                    if i < len(chapters):
                        ch = chapters[i]
                        parsed_chapters.append({
                            "content": ch.get("content", ""),
                            "knowledge_points": ch.get("knowledge_points", []),
                            "illustration_prompt": ch.get("illustration_prompt") if include_illustration else None,
                        })
                    else:
                        parsed_chapters.append({
                            "content": f"这是关于{topic}的精彩内容。",
                            "knowledge_points": [],
                            "illustration_prompt": None,
                        })
                return parsed_chapters
        except json.JSONDecodeError:
            pass

        # 解析失败时返回默认值
        return [
            {
                "content": f"这是关于{topic}的第{i+1}章内容。",
                "knowledge_points": [],
                "illustration_prompt": None,
            }
            for i in range(chapter_count)
        ]
