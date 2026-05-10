"""绘本生成器核心逻辑测试"""

from unittest.mock import AsyncMock, patch

import pytest

from guige_picbook.core.generator import PictureBookGenerator
from guige_picbook.core.models import BookConfig, Language
from guige_picbook.utils.config import LLMProvider, Settings


@pytest.fixture
def settings():
    return Settings(
        default_llm_provider=LLMProvider.ANTHROPIC,
        anthropic_api_key="test-key",
    )


@pytest.fixture
def generator(settings):
    return PictureBookGenerator(settings)


class TestPictureBookGenerator:
    @pytest.mark.asyncio
    async def test_generate_full_pipeline(self, generator):
        """测试完整的生成流程"""
        config = BookConfig(
            topic="恐龙",
            language=Language.CHINESE,
            age_range=(7, 10),
            chapter_count=3,
        )

        mock_knowledge = {
            "topic": "恐龙",
            "content": ["恐龙相关知识"],
            "sources": ["https://example.com"],
        }

        mock_adapted = {
            "summary": "适配后的恐龙知识",
            "sources": ["https://example.com"],
        }

        mock_structure = {
            "title": "恐龙大冒险",
            "summary": "一本关于恐龙的绘本",
            "chapters": ["恐龙时代", "恐龙种类", "恐龙灭绝"],
        }

        mock_chapters = [
            {"content": f"第{i+1}章内容", "knowledge_points": [f"知识点{i+1}"]}
            for i in range(3)
        ]

        with (
            patch(
                "guige_picbook.core.generator.KnowledgeSearchService"
            ) as mock_search_cls,
            patch.object(
                generator.content_adapter, "adapt", new_callable=AsyncMock
            ) as mock_adapt,
            patch.object(
                generator.content_adapter,
                "generate_book_structure",
                new_callable=AsyncMock,
            ) as mock_gen_structure,
            patch.object(
                generator.content_adapter,
                "generate_all_chapters",
                new_callable=AsyncMock,
            ) as mock_gen_chapters,
        ):
            # 设置 KnowledgeSearchService mock
            mock_search_instance = AsyncMock()
            mock_search_instance.search.return_value = mock_knowledge
            mock_search_instance.__aenter__ = AsyncMock(return_value=mock_search_instance)
            mock_search_instance.__aexit__ = AsyncMock(return_value=False)
            mock_search_cls.return_value = mock_search_instance

            mock_adapt.return_value = mock_adapted
            mock_gen_structure.return_value = mock_structure
            mock_gen_chapters.return_value = mock_chapters

            book = await generator.generate(config)

        assert book.title == "恐龙大冒险"
        assert book.topic == "恐龙"
        assert book.language == Language.CHINESE
        assert len(book.chapters) == 3
        assert book.chapters[0].content == "第1章内容"
        assert book.chapters[0].knowledge_points == ["知识点1"]
        assert book.sources == ["https://example.com"]

    @pytest.mark.asyncio
    async def test_generate_english_book(self, generator):
        """测试英文绘本生成"""
        config = BookConfig(
            topic="Space",
            language=Language.ENGLISH,
            age_range=(8, 12),
            chapter_count=3,
        )

        mock_knowledge = {
            "topic": "Space",
            "content": ["Space facts"],
            "sources": [],
        }

        mock_adapted = {"summary": "Adapted space content", "sources": []}

        mock_structure = {
            "title": "Space Adventure",
            "summary": "A fun book about space",
            "chapters": ["The Sun", "Planets", "Stars"],
        }

        mock_chapters = [
            {"content": f"Chapter {i+1} content", "knowledge_points": [f"Fact {i+1}"]}
            for i in range(3)
        ]

        with (
            patch(
                "guige_picbook.core.generator.KnowledgeSearchService"
            ) as mock_search_cls,
            patch.object(
                generator.content_adapter, "adapt", new_callable=AsyncMock
            ) as mock_adapt,
            patch.object(
                generator.content_adapter,
                "generate_book_structure",
                new_callable=AsyncMock,
            ) as mock_gen_structure,
            patch.object(
                generator.content_adapter,
                "generate_all_chapters",
                new_callable=AsyncMock,
            ) as mock_gen_chapters,
        ):
            mock_search_instance = AsyncMock()
            mock_search_instance.search.return_value = mock_knowledge
            mock_search_instance.__aenter__ = AsyncMock(return_value=mock_search_instance)
            mock_search_instance.__aexit__ = AsyncMock(return_value=False)
            mock_search_cls.return_value = mock_search_instance

            mock_adapt.return_value = mock_adapted
            mock_gen_structure.return_value = mock_structure
            mock_gen_chapters.return_value = mock_chapters

            book = await generator.generate(config)

        assert book.title == "Space Adventure"
        assert book.language == Language.ENGLISH
        assert book.target_age == "Ages 8-12"

    @pytest.mark.asyncio
    async def test_to_markdown_output(self, generator):
        """测试生成的绘本能正确导出为Markdown"""
        config = BookConfig(topic="Ocean", language=Language.ENGLISH, chapter_count=3)

        mock_knowledge = {"topic": "Ocean", "content": ["Ocean info"], "sources": []}
        mock_adapted = {"summary": "Ocean content", "sources": []}
        mock_structure = {
            "title": "Ocean World",
            "summary": "About the ocean",
            "chapters": ["Waves", "Fish", "Coral"],
        }
        mock_chapters = [
            {"content": f"Content {i+1}", "knowledge_points": []}
            for i in range(3)
        ]

        with (
            patch(
                "guige_picbook.core.generator.KnowledgeSearchService"
            ) as mock_search_cls,
            patch.object(
                generator.content_adapter, "adapt", new_callable=AsyncMock
            ) as mock_adapt,
            patch.object(
                generator.content_adapter,
                "generate_book_structure",
                new_callable=AsyncMock,
            ) as mock_gen_structure,
            patch.object(
                generator.content_adapter,
                "generate_all_chapters",
                new_callable=AsyncMock,
            ) as mock_gen_chapters,
        ):
            mock_search_instance = AsyncMock()
            mock_search_instance.search.return_value = mock_knowledge
            mock_search_instance.__aenter__ = AsyncMock(return_value=mock_search_instance)
            mock_search_instance.__aexit__ = AsyncMock(return_value=False)
            mock_search_cls.return_value = mock_search_instance

            mock_adapt.return_value = mock_adapted
            mock_gen_structure.return_value = mock_structure
            mock_gen_chapters.return_value = mock_chapters

            book = await generator.generate(config)

        md = book.to_markdown()
        assert "# Ocean World" in md
        assert "## Chapter 1: Waves" in md
        assert "Content 1" in md
