"""内容适配服务测试"""

import json
from unittest.mock import AsyncMock, patch

import pytest

from guige_picbook.services.content_adapter import ContentAdapterService
from guige_picbook.utils.config import Language, LLMProvider, Settings


@pytest.fixture
def settings():
    return Settings(
        default_llm_provider=LLMProvider.ANTHROPIC,
        anthropic_api_key="test-key",
    )


@pytest.fixture
def service(settings):
    return ContentAdapterService(settings)


class TestAdapt:
    @pytest.mark.asyncio
    async def test_adapt_with_content(self, service):
        """测试有搜索结果时的内容适配"""
        knowledge = {
            "topic": "恐龙",
            "content": ["恐龙是一类主要的爬行动物"],
            "sources": ["https://example.com"],
        }

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "适配后的儿童友好内容"
            result = await service.adapt(
                knowledge=knowledge,
                age_range=(7, 10),
                language=Language.CHINESE,
            )

        assert result["summary"] == "适配后的儿童友好内容"
        assert result["sources"] == ["https://example.com"]
        mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_adapt_without_content(self, service):
        """测试无搜索结果时从零生成"""
        knowledge = {"topic": "恐龙", "content": [], "sources": []}

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "从零生成的内容"
            result = await service.adapt(
                knowledge=knowledge,
                age_range=(7, 10),
                language=Language.CHINESE,
            )

        assert result["summary"] == "从零生成的内容"
        assert result["sources"] == ["AI generated content"]


class TestGenerateBookStructure:
    @pytest.mark.asyncio
    async def test_parse_valid_json(self, service):
        """测试正确解析含嵌套数组的JSON"""
        llm_response = json.dumps({
            "title": "恐龙大冒险",
            "summary": "一本有趣的恐龙绘本",
            "chapters": ["恐龙时代", "恐龙种类", "恐龙灭绝"],
        })

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = llm_response
            result = await service.generate_book_structure(
                topic="恐龙",
                language=Language.CHINESE,
                age_range=(7, 10),
                chapter_count=3,
                adapted_content="适配内容",
            )

        assert result["title"] == "恐龙大冒险"
        assert result["summary"] == "一本有趣的恐龙绘本"
        assert len(result["chapters"]) == 3

    @pytest.mark.asyncio
    async def test_parse_json_with_surrounding_text(self, service):
        """测试LLM返回JSON前后有额外文字时能正确解析"""
        llm_response = (
            'Here is the structure:\n'
            '{"title": "Ocean World", "summary": "A fun book", "chapters": ["Ch1", "Ch2"]}'
            '\nHope this helps!'
        )

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = llm_response
            result = await service.generate_book_structure(
                topic="ocean",
                language=Language.ENGLISH,
                age_range=(7, 10),
                chapter_count=2,
                adapted_content="content",
            )

        assert result["title"] == "Ocean World"
        assert len(result["chapters"]) == 2

    @pytest.mark.asyncio
    async def test_fallback_on_invalid_json(self, service):
        """测试JSON解析失败时返回默认值"""
        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "这不是有效的JSON"
            result = await service.generate_book_structure(
                topic="恐龙",
                language=Language.CHINESE,
                age_range=(7, 10),
                chapter_count=3,
                adapted_content="content",
            )

        assert "恐龙" in result["title"]
        assert len(result["chapters"]) == 3

    @pytest.mark.asyncio
    async def test_fill_missing_chapters(self, service):
        """测试章节数不足时自动补充"""
        llm_response = json.dumps({
            "title": "太空探险",
            "summary": "太空绘本",
            "chapters": ["星星"],
        })

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = llm_response
            result = await service.generate_book_structure(
                topic="太空",
                language=Language.CHINESE,
                age_range=(7, 10),
                chapter_count=3,
                adapted_content="content",
            )

        assert len(result["chapters"]) == 3


class TestGenerateAllChapters:
    @pytest.mark.asyncio
    async def test_parse_chapters_json(self, service):
        """测试正确解析章节内容JSON"""
        llm_response = json.dumps({
            "chapters": [
                {
                    "content": "第一章内容",
                    "knowledge_points": ["知识点1"],
                    "illustration_prompt": "A dinosaur scene",
                },
                {
                    "content": "第二章内容",
                    "knowledge_points": ["知识点2", "知识点3"],
                    "illustration_prompt": "A forest scene",
                },
            ]
        })

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = llm_response
            result = await service.generate_all_chapters(
                topic="恐龙",
                chapter_titles=["恐龙时代", "恐龙世界"],
                language=Language.CHINESE,
                age_range=(7, 10),
                adapted_content="适配内容",
            )

        assert len(result) == 2
        assert result[0]["content"] == "第一章内容"
        assert result[1]["knowledge_points"] == ["知识点2", "知识点3"]

    @pytest.mark.asyncio
    async def test_fallback_on_invalid_json(self, service):
        """测试JSON解析失败时返回默认值"""
        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "无效JSON"
            result = await service.generate_all_chapters(
                topic="恐龙",
                chapter_titles=["Ch1", "Ch2"],
                language=Language.CHINESE,
                age_range=(7, 10),
                adapted_content="content",
            )

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_generate_many_pages_in_batches(self, service):
        """测试30页内容按批生成，避免单次响应过大"""
        chapter_titles = [f"Page {i + 1}" for i in range(12)]
        batch_responses = []
        for start, count in [(0, 5), (5, 5), (10, 2)]:
            batch_responses.append(json.dumps({
                "chapters": [
                    {
                        "content": f"Page {start + i + 1} content",
                        "knowledge_points": [f"Fact {start + i + 1}"],
                    }
                    for i in range(count)
                ]
            }))

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = batch_responses
            result = await service.generate_all_chapters(
                topic="space",
                chapter_titles=chapter_titles,
                language=Language.ENGLISH,
                age_range=(8, 12),
                adapted_content="content",
                include_illustration=False,
            )

        assert len(result) == 12
        assert result[0]["content"] == "Page 1 content"
        assert result[-1]["content"] == "Page 12 content"
        assert mock_llm.call_count == 3

    @pytest.mark.asyncio
    async def test_default_illustration_aspect_ratio_is_3_by_4(self, service):
        """测试默认插图提示使用3:4竖版比例。"""
        llm_response = json.dumps({
            "chapters": [
                {
                    "content": "Page content",
                    "knowledge_points": ["Fact"],
                    "illustration_prompt": "A child-friendly science scene",
                }
            ]
        })

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = llm_response
            await service.generate_all_chapters(
                topic="space",
                chapter_titles=["Page 1"],
                language=Language.ENGLISH,
                age_range=(8, 12),
                adapted_content="content",
            )

        prompt = mock_llm.call_args.args[0]
        assert "3:4 portrait aspect ratio" in prompt
        assert "9:16 portrait aspect ratio" not in prompt


class TestGenerateSocialCaptions:
    @pytest.mark.asyncio
    async def test_parse_captions(self, service):
        """测试正确解析双语文案"""
        llm_response = json.dumps({
            "zh": "一本关于恐龙的绘本",
            "en": "A picture book about dinosaurs",
        })

        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = llm_response
            result = await service.generate_social_captions(
                topic="恐龙",
                book_title="恐龙大冒险",
                summary="恐龙简介",
                language=Language.CHINESE,
            )

        assert result["zh"] == "一本关于恐龙的绘本"
        assert result["en"] == "A picture book about dinosaurs"

    @pytest.mark.asyncio
    async def test_fallback_on_invalid_response(self, service):
        """测试解析失败时返回默认文案"""
        with patch.object(service, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "not json"
            result = await service.generate_social_captions(
                topic="恐龙",
                book_title="恐龙大冒险",
                summary="简介",
                language=Language.CHINESE,
            )

        assert "恐龙" in result["zh"]
        assert "dinosaur" in result["en"].lower() or "恐龙" in result["en"]
