"""数据模型测试"""


from guige_picbook.core.models import (
    BookConfig,
    Chapter,
    Language,
    PictureBook,
)


class TestBookConfig:
    def test_default_values(self):
        config = BookConfig(topic="恐龙")
        assert config.topic == "恐龙"
        assert config.language == Language.ENGLISH
        assert config.age_range == (7, 10)
        assert config.chapter_count == 5

    def test_custom_values(self):
        config = BookConfig(
            topic="Space",
            language=Language.ENGLISH,
            age_range=(8, 12),
            chapter_count=8,
        )
        assert config.topic == "Space"
        assert config.language == Language.ENGLISH
        assert config.age_range == (8, 12)
        assert config.chapter_count == 8


class TestChapter:
    def test_chapter_creation(self):
        chapter = Chapter(
            number=1,
            title="认识恐龙",
            content="很久很久以前，地球上生活着一群巨大的动物...",
            illustration_prompt="一群恐龙在森林中漫步的场景",
            knowledge_points=["恐龙生活在中生代", "恐龙有很多种类"],
        )
        assert chapter.number == 1
        assert chapter.title == "认识恐龙"
        assert len(chapter.knowledge_points) == 2


class TestPictureBook:
    def test_to_markdown(self):
        book = PictureBook(
            title="恐龙世界大冒险",
            topic="恐龙",
            language=Language.CHINESE,
            target_age="7-10岁",
            summary="这是一本关于恐龙的有趣绘本。",
            chapters=[
                Chapter(
                    number=1,
                    title="恐龙时代",
                    content="很久以前...",
                    knowledge_points=["恐龙很大"],
                )
            ],
            sources=["维基百科"],
        )

        markdown = book.to_markdown()
        assert "# 恐龙世界大冒险" in markdown
        assert "**主题**: 恐龙" in markdown
        assert "## 第1章: 恐龙时代" in markdown
        assert "## 参考来源" in markdown
