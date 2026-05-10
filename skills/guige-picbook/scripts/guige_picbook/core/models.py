"""数据模型定义"""

from typing import Optional

from pydantic import BaseModel, Field

from ..utils.config import Language


class BookConfig(BaseModel):
    """绘本配置"""

    topic: str = Field(..., description="绘本主题")
    language: Language = Field(default=Language.ENGLISH, description="目标语言")
    age_range: tuple[int, int] = Field(default=(7, 10), description="目标年龄范围")
    chapter_count: int = Field(default=5, ge=3, le=10, description="章节数量")
    include_illustrations: bool = Field(default=True, description="是否包含插图描述")


class Chapter(BaseModel):
    """绘本章节"""

    number: int = Field(..., description="章节编号")
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    illustration_prompt: Optional[str] = Field(None, description="插图生成提示词")
    knowledge_points: list[str] = Field(default_factory=list, description="知识要点")


class PictureBook(BaseModel):
    """绘本成品"""

    title: str = Field(..., description="绘本标题")
    topic: str = Field(..., description="主题")
    language: Language = Field(..., description="语言")
    target_age: str = Field(..., description="目标年龄")
    summary: str = Field(..., description="内容简介")
    chapters: list[Chapter] = Field(default_factory=list, description="章节列表")
    sources: list[str] = Field(default_factory=list, description="知识来源")

    def _get_labels(self) -> dict:
        """获取对应语言的标签"""
        labels = {
            Language.ENGLISH: {
                "topic": "Topic",
                "age": "Target Age",
                "language": "Language",
                "summary": "Summary",
                "chapter": "Chapter",
                "illustration": "Illustration",
                "knowledge": "Key Points",
                "sources": "References",
            },
            Language.CHINESE: {
                "topic": "主题",
                "age": "适合年龄",
                "language": "语言",
                "summary": "简介",
                "chapter": "第{}章",
                "illustration": "插图描述",
                "knowledge": "知识要点",
                "sources": "参考来源",
            },
            Language.JAPANESE: {
                "topic": "テーマ",
                "age": "対象年齢",
                "language": "言語",
                "summary": "あらすじ",
                "chapter": "第{}章",
                "illustration": "イラスト",
                "knowledge": "ポイント",
                "sources": "参考文献",
            },
            Language.KOREAN: {
                "topic": "주제",
                "age": "대상 연령",
                "language": "언어",
                "summary": "소개",
                "chapter": "제{}장",
                "illustration": "삽화 설명",
                "knowledge": "핵심 포인트",
                "sources": "참고 자료",
            },
        }
        return labels.get(self.language, labels[Language.ENGLISH])

    def to_markdown(self) -> str:
        """导出为Markdown格式"""
        labels = self._get_labels()

        lines = [
            f"# {self.title}",
            "",
            f"**{labels['topic']}**: {self.topic}",
            f"**{labels['age']}**: {self.target_age}",
            f"**{labels['language']}**: {self.language.value}",
            "",
            f"## {labels['summary']}",
            self.summary,
            "",
        ]

        for chapter in self.chapters:
            # 格式化章节标题
            if self.language == Language.ENGLISH:
                chapter_header = f"## {labels['chapter']} {chapter.number}: {chapter.title}"
            else:
                chapter_header = f"## {labels['chapter'].format(chapter.number)}: {chapter.title}"

            lines.extend(
                [
                    chapter_header,
                    "",
                    chapter.content,
                    "",
                ]
            )
            if chapter.illustration_prompt:
                lines.extend(
                    [
                        f"*{labels['illustration']}: {chapter.illustration_prompt}*",
                        "",
                    ]
                )
            if chapter.knowledge_points:
                lines.append(f"**{labels['knowledge']}:**")
                for point in chapter.knowledge_points:
                    lines.append(f"- {point}")
                lines.append("")

        if self.sources:
            lines.extend([f"## {labels['sources']}", ""])
            for source in self.sources:
                lines.append(f"- {source}")

        return "\n".join(lines)
