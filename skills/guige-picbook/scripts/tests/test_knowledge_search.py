"""知识搜索服务测试"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from guige_picbook.services.knowledge_search import KnowledgeSearchService
from guige_picbook.utils.config import Settings


def _mock_wikipedia_response(extract: str, page_url: str) -> httpx.Response:
    """构造模拟的 Wikipedia API 响应"""
    return httpx.Response(
        200,
        json={
            "extract": extract,
            "content_urls": {"desktop": {"page": page_url}},
        },
        request=httpx.Request("GET", "https://en.wikipedia.org/api/rest_v1/page/summary/test"),
    )


def _mock_wikipedia_search_response(title: str) -> httpx.Response:
    """构造模拟的 Wikipedia 搜索 API 响应"""
    return httpx.Response(
        200,
        json={"query": {"search": [{"title": title}]}},
        request=httpx.Request("GET", "https://en.wikipedia.org/w/api.php"),
    )


class TestKnowledgeSearchService:
    @pytest.fixture
    def settings(self):
        return Settings()

    @pytest.fixture
    def service(self, settings):
        return KnowledgeSearchService(settings)

    @pytest.mark.asyncio
    async def test_search_wikipedia(self, service):
        """测试维基百科搜索"""
        mock_resp = _mock_wikipedia_response(
            "Dinosaurs are a diverse group of reptiles.",
            "https://en.wikipedia.org/wiki/Dinosaur",
        )
        with patch.object(service.client, "get", new_callable=AsyncMock, return_value=mock_resp):
            result = await service._search_wikipedia("恐龙")

        assert "content" in result
        assert "sources" in result
        assert len(result["content"]) > 0

    @pytest.mark.asyncio
    async def test_search_wikipedia_english(self, service):
        """测试英文维基百科搜索"""
        mock_resp = _mock_wikipedia_response(
            "Dinosaurs are a diverse group of reptiles of the clade Dinosauria.",
            "https://en.wikipedia.org/wiki/Dinosaur",
        )
        with patch.object(service.client, "get", new_callable=AsyncMock, return_value=mock_resp):
            result = await service._fetch_wikipedia_page("Dinosaur", "en")

        assert result is not None
        assert "content" in result
        assert "dinosaur" in result["content"].lower()

    @pytest.mark.asyncio
    async def test_search_combined(self, service):
        """测试组合搜索"""
        mock_resp = _mock_wikipedia_response(
            "The Solar System is the gravitationally bound system.",
            "https://en.wikipedia.org/wiki/Solar_System",
        )
        # 确保不调用 Tavily/SerpAPI
        service.settings.tavily_api_key = ""
        service.settings.serp_api_key = ""
        with patch.object(service.client, "get", new_callable=AsyncMock, return_value=mock_resp):
            result = await service.search("太阳系")

        assert "topic" in result
        assert result["topic"] == "太阳系"
        assert "content" in result
        assert "sources" in result

    @pytest.mark.asyncio
    async def test_search_nonexistent_topic(self, service):
        """测试不存在的主题"""
        mock_404 = httpx.Response(
            404,
            request=httpx.Request("GET", "https://en.wikipedia.org/api/rest_v1/page/summary/x"),
        )
        mock_empty_search = httpx.Response(
            200,
            json={"query": {"search": []}},
            request=httpx.Request("GET", "https://en.wikipedia.org/w/api.php"),
        )

        call_count = 0

        async def mock_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_404
            return mock_empty_search

        with patch.object(service.client, "get", side_effect=mock_get):
            result = await service._search_wikipedia("这个主题肯定不存在12345xyz")

        assert "content" in result
        assert "sources" in result
        assert len(result["content"]) == 0

    @pytest.mark.asyncio
    async def test_tavily_without_api_key(self, service):
        """测试没有API密钥时Tavily返回空结果"""
        service.settings.tavily_api_key = ""
        result = await service._search_tavily("恐龙")

        assert result == {"content": [], "sources": []}

    @pytest.mark.asyncio
    async def test_serpapi_without_api_key(self, service):
        """测试没有API密钥时SerpAPI返回空结果"""
        service.settings.serp_api_key = ""
        result = await service._search_serpapi("恐龙")

        assert result == {"content": [], "sources": []}

    @pytest.mark.asyncio
    async def test_close(self, service):
        """测试关闭HTTP客户端"""
        await service.close()
        assert service.client.is_closed
