"""知识搜索服务 - 根据主题搜索相关知识"""

import asyncio
from urllib.parse import quote

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..utils.config import Settings


class KnowledgeSearchService:
    """知识搜索服务

    负责根据用户输入的主题搜索相关知识和信息。
    支持多种搜索源:
    - Tavily (AI优化搜索)
    - SerpAPI (Google搜索)
    - 维基百科
    """

    TAVILY_API_URL = "https://api.tavily.com/search"
    SERPAPI_API_URL = "https://serpapi.com/search"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def search(self, topic: str, max_results: int = 5) -> dict:
        """搜索主题相关知识

        优先级: Tavily > SerpAPI > Wikipedia
        如果配置了多个API，会并行搜索并合并结果

        Args:
            topic: 搜索主题
            max_results: 每个搜索源的最大结果数

        Returns:
            包含知识内容、来源等信息的字典
        """
        results = {
            "topic": topic,
            "content": [],
            "sources": [],
        }

        # 收集所有可用的搜索任务
        tasks = []

        # Tavily搜索 (优先)
        if self.settings.tavily_api_key:
            tasks.append(self._search_tavily(topic, max_results))

        # SerpAPI搜索
        if self.settings.serp_api_key:
            tasks.append(self._search_serpapi(topic, max_results))

        # 维基百科搜索 (始终执行)
        tasks.append(self._search_wikipedia(topic))

        # 并行执行所有搜索
        search_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        for result in search_results:
            if isinstance(result, Exception):
                continue
            results["content"].extend(result.get("content", []))
            results["sources"].extend(result.get("sources", []))

        return results

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _search_tavily(self, topic: str, max_results: int = 5) -> dict:
        """Tavily搜索 - AI优化的搜索API

        特点:
        - 专为LLM/RAG应用优化
        - 返回结构化、清洁的内容
        - 支持深度搜索模式

        Args:
            topic: 搜索主题
            max_results: 最大结果数

        Returns:
            搜索结果
        """
        if not self.settings.tavily_api_key:
            return {"content": [], "sources": []}

        # 为儿童绘本优化搜索查询 - 使用英文搜索获取更准确的知识
        search_query = f"{topic} children education science facts for kids"

        payload = {
            "api_key": self.settings.tavily_api_key,
            "query": search_query,
            "search_depth": "advanced",  # 深度搜索获取更多内容
            "include_answer": True,  # 包含AI生成的答案摘要
            "include_raw_content": False,
            "max_results": max_results,
            "include_domains": [],  # 可以限制特定域名
            "exclude_domains": [],
        }

        try:
            response = await self.client.post(
                self.TAVILY_API_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

            content = []
            sources = []

            # 添加AI生成的答案摘要
            if data.get("answer"):
                content.append(f"[Tavily摘要] {data['answer']}")

            # 添加搜索结果
            for result in data.get("results", []):
                if result.get("content"):
                    content.append(result["content"])
                if result.get("url"):
                    sources.append(result["url"])

            return {"content": content, "sources": sources}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("Tavily API密钥无效")
            raise
        except Exception:
            return {"content": [], "sources": []}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _search_serpapi(self, topic: str, max_results: int = 5) -> dict:
        """SerpAPI搜索 - Google搜索结果API

        特点:
        - 获取真实的Google搜索结果
        - 支持多种搜索引擎
        - 丰富的结果元数据

        Args:
            topic: 搜索主题
            max_results: 最大结果数

        Returns:
            搜索结果
        """
        if not self.settings.serp_api_key:
            return {"content": [], "sources": []}

        # 为儿童绘本优化搜索查询 - 使用英文搜索获取更准确的知识
        search_query = f"{topic} children education science facts for kids"

        params = {
            "api_key": self.settings.serp_api_key,
            "q": search_query,
            "engine": "google",
            "hl": "en",  # 英文结果
            "gl": "us",  # 美国地区
            "num": max_results,
            "safe": "active",  # 安全搜索，过滤不适合儿童的内容
        }

        try:
            response = await self.client.get(self.SERPAPI_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            content = []
            sources = []

            # 提取知识图谱信息 (如果有)
            if data.get("knowledge_graph"):
                kg = data["knowledge_graph"]
                if kg.get("description"):
                    content.append(f"[知识图谱] {kg['description']}")
                if kg.get("source", {}).get("link"):
                    sources.append(kg["source"]["link"])

            # 提取精选摘要 (如果有)
            if data.get("answer_box"):
                ab = data["answer_box"]
                if ab.get("answer"):
                    content.append(f"[精选答案] {ab['answer']}")
                elif ab.get("snippet"):
                    content.append(f"[精选摘要] {ab['snippet']}")

            # 提取有机搜索结果
            for result in data.get("organic_results", [])[:max_results]:
                if result.get("snippet"):
                    content.append(result["snippet"])
                if result.get("link"):
                    sources.append(result["link"])

            return {"content": content, "sources": sources}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("SerpAPI密钥无效")
            raise
        except Exception:
            return {"content": [], "sources": []}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _search_wikipedia(self, topic: str) -> dict:
        """维基百科搜索

        仅使用英文维基百科获取准确的知识内容

        Args:
            topic: 搜索主题

        Returns:
            搜索结果
        """
        content = []
        sources = []

        # 仅使用英文维基百科获取准确的知识内容
        en_result = await self._fetch_wikipedia_page(topic, "en")
        if en_result:
            content.append(f"[Wikipedia] {en_result['content']}")
            sources.append(en_result["url"])

        return {"content": content, "sources": sources}

    async def _fetch_wikipedia_page(self, topic: str, lang: str = "en") -> dict | None:
        """获取维基百科页面摘要

        Args:
            topic: 搜索主题
            lang: 语言代码 (zh, en)

        Returns:
            页面内容和URL，如果未找到返回None
        """
        try:
            encoded_topic = quote(topic)
            url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_topic}"
            response = await self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                extract = data.get("extract", "")
                page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")

                if extract:
                    return {"content": extract, "url": page_url}

            # 如果直接查找失败，尝试搜索
            search_url = f"https://{lang}.wikipedia.org/w/api.php"
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": topic,
                "format": "json",
                "srlimit": 1,
            }
            search_response = await self.client.get(search_url, params=search_params)

            if search_response.status_code == 200:
                search_data = search_response.json()
                results = search_data.get("query", {}).get("search", [])

                if results:
                    # 获取第一个搜索结果的页面
                    page_title = results[0]["title"]
                    encoded_title = quote(page_title)
                    page_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
                    page_response = await self.client.get(page_url)

                    if page_response.status_code == 200:
                        page_data = page_response.json()
                        return {
                            "content": page_data.get("extract", ""),
                            "url": page_data.get("content_urls", {})
                            .get("desktop", {})
                            .get("page", ""),
                        }

        except Exception:
            pass

        return None

    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
