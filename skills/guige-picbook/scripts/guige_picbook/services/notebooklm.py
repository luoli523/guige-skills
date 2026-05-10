"""NotebookLM服务 - 集成Google NotebookLM生成最终绘本"""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

from ..utils.config import Settings

# notebooklm-py 是可选依赖
try:
    from notebooklm import NotebookLMClient
    from notebooklm.types import GenerationStatus

    NOTEBOOKLM_AVAILABLE = True
except ImportError:
    NOTEBOOKLM_AVAILABLE = False

# Default notebook name. Can be overridden with NOTEBOOKLM_NOTEBOOK_NAME.
DEFAULT_NOTEBOOK_NAME = "儿童绘本"


class NotebookLMService:
    """NotebookLM服务

    负责将生成的绘本内容上传到Google NotebookLM，
    利用其功能生成:
    - Slides (演示文稿)
    - 音频播客版本
    - Quiz
    - Flashcards
    - 思维导图

    使用前需要:
    1. pip install -r skills/guige-picbook/scripts/requirements-notebooklm.txt
    2. notebooklm login  # 命令行登录
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.notebook_name = settings.notebooklm_notebook_name or DEFAULT_NOTEBOOK_NAME

    def _check_notebooklm(self):
        """检查notebooklm-py是否可用"""
        if not NOTEBOOKLM_AVAILABLE:
            raise ImportError(
                "notebooklm-py未安装。请运行:\n"
                "  pip install -r skills/guige-picbook/scripts/requirements-notebooklm.txt\n"
                "  notebooklm login  # 首次使用需要登录"
            )

    async def _wait_with_progress(
        self,
        client: NotebookLMClient,
        notebook_id: str,
        task_id: str,
        task_name: str = "任务",
        check_interval: int = 5,
        max_wait_time: int = 600,
    ) -> GenerationStatus:
        """等待任务完成，显示进度

        Args:
            client: NotebookLM客户端
            notebook_id: 笔记本ID
            task_id: 任务ID
            task_name: 任务名称（用于显示）
            check_interval: 检查间隔（秒）
            max_wait_time: 最大等待时间（秒）

        Returns:
            GenerationStatus 对象

        Raises:
            TimeoutError: 超时
            Exception: 生成失败
        """
        elapsed = 0
        dots = 0

        while elapsed < max_wait_time:
            try:
                # 使用 poll_status 检查状态
                status = await client.artifacts.poll_status(notebook_id, task_id)

                if status.is_complete:
                    print(f"\n✓ {task_name}完成")
                    return status
                elif status.is_failed:
                    error_msg = status.error or "未知错误"
                    print(f"\n✗ {task_name}失败: {error_msg}")
                    raise Exception(f"{task_name}失败: {error_msg}")
                elif status.is_rate_limited:
                    print("\n⚠️  API 请求频率受限，等待重试...")
                    await asyncio.sleep(check_interval * 2)  # 受限时等待更久
                    elapsed += check_interval * 2
                elif status.is_pending or status.is_in_progress:
                    # 显示进度动画
                    dots = (dots + 1) % 4
                    progress = "." * dots + " " * (3 - dots)
                    print(
                        f"\r  等待中{progress} (已等待 {elapsed}秒)", end="", flush=True
                    )

                    # 等待一段时间再检查
                    await asyncio.sleep(check_interval)
                    elapsed += check_interval
                else:
                    # 未知状态
                    print("\n  未知状态，继续等待...")
                    await asyncio.sleep(check_interval)
                    elapsed += check_interval

            except Exception as e:
                if "not found" in str(e).lower() or "404" in str(e):
                    raise Exception(f"{task_name}不存在或已过期")
                # 其他异常继续抛出
                raise

        # 超时
        raise TimeoutError(
            f"{task_name}超时（已等待{max_wait_time}秒）。\n"
            f"你可以稍后手动检查: https://notebooklm.google.com/notebook/{notebook_id}"
        )

    async def _find_or_create_notebook(
        self, client: NotebookLMClient, notebook_name: str | None = None
    ) -> str:
        """查找或创建指定名称的 notebook

        Args:
            client: NotebookLM 客户端
            notebook_name: notebook 名称

        Returns:
            notebook ID
        """
        notebook_name = notebook_name or self.notebook_name

        # 列出所有 notebooks
        notebooks = await client.notebooks.list()

        # 查找同名 notebook
        for nb in notebooks:
            if nb.title == notebook_name:
                print(f"✓ 找到已存在的 notebook: {notebook_name} (ID: {nb.id})")
                return nb.id

        # 不存在，创建新的
        print(f"未找到 notebook '{notebook_name}'，正在创建...")
        notebook = await client.notebooks.create(notebook_name)
        print(f"✓ 创建 notebook: {notebook.title} (ID: {notebook.id})")
        return notebook.id

    async def login(self) -> None:
        """登录说明

        notebooklm-py 使用命令行登录，请在终端运行:
        notebooklm login
        """
        self._check_notebooklm()
        print("\n请在终端运行以下命令登录 NotebookLM:")
        print("  notebooklm login")
        print("\n登录后会打开浏览器完成授权。")

    async def upload(
        self, content: str, title: str = "Picture Book"
    ) -> tuple[str, str, str]:
        """上传内容到NotebookLM的"儿童绘本" notebook

        Args:
            content: Markdown格式的绘本内容
            title: 源文件标题（用作文件名）

        Returns:
            (notebook_id, source_id, source_title) 元组
        """
        self._check_notebooklm()

        print("[1/4] 准备上传内容...")

        async with await NotebookLMClient.from_storage() as client:
            # 查找或创建"儿童绘本" notebook
            print("[2/4] 查找或创建 notebook...")
            notebook_id = await self._find_or_create_notebook(client)

            # 检查是否已存在同名文件
            print("[3/4] 检查已有文件...")
            sources = await client.sources.list(notebook_id)
            existing_names = {src.title for src in sources}

            # 生成唯一的文件名（保留 .md 后缀）
            source_title = title
            if source_title in existing_names:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # 如果文件名包含 .md 后缀，在后缀前插入时间戳
                if title.endswith(".md"):
                    base_name = title[:-3]  # 去掉 .md
                    source_title = f"{base_name}_{timestamp}.md"
                else:
                    source_title = f"{title}_{timestamp}"
                print(f"    检测到同名文件，添加时间戳: {source_title}")

            # 创建临时 Markdown 文件
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False, encoding="utf-8"
            ) as f:
                f.write(content)
                temp_file = f.name

            try:
                # 上传文件作为源
                print(f"[4/4] 上传文件 '{source_title}' 并等待处理...")
                print("    正在上传...", end="", flush=True)

                # 上传并等待处理完成（最多等待2分钟）
                source = await client.sources.add_file(
                    notebook_id, temp_file, wait=True, wait_timeout=120.0
                )

                # 重命名为目标名称（如果需要）
                if source.title != source_title:
                    await client.sources.rename(notebook_id, source.id, source_title)

                print(f"\r✓ 上传文件完成: {source_title}" + " " * 20)
                print(f"    Source ID: {source.id}")

                return notebook_id, source.id, source_title

            except asyncio.TimeoutError:
                print("\n✗ 上传超时")
                raise Exception("文件上传或处理超时，请稍后重试")
            except Exception as e:
                print(f"\n✗ 上传失败: {e}")
                raise
            finally:
                Path(temp_file).unlink(missing_ok=True)

    async def generate_slides(
        self,
        notebook_id: str,
        source_ids: list[str] | None = None,
        source_title: str | None = None,
        download_dir: str | None = None,
        instructions: str | None = "创建适合儿童和少年阅读的，卡通风格",
        language: str = "en",
        slide_format: str | None = "detailed",
        slide_length: str | None = "default",
    ) -> str:
        """生成Slides并下载

        Args:
            notebook_id: NotebookLM笔记本ID
            source_ids: 要使用的源文件ID列表（None 表示使用所有源文件）
            source_title: 源文件标题（用于命名输出文件，None 时使用 notebook ID）
            download_dir: 下载目录，默认为当前目录
            instructions: 自定义生成指令，默认："创建适合儿童和少年阅读的，卡通风格"
            language: 语言代码，默认 'en'
            slide_format: 格式（'detailed' 或 'presenter'），默认 'detailed'
            slide_length: 长度（'short' 或 'default'），默认 'default'

        Returns:
            下载的文件路径
        """
        self._check_notebooklm()

        # 导入枚举类型
        from notebooklm.rpc.types import SlideDeckFormat, SlideDeckLength

        download_path = Path(download_dir) if download_dir else Path.cwd()
        download_path.mkdir(parents=True, exist_ok=True)

        async with await NotebookLMClient.from_storage() as client:
            print("[1/3] 正在生成 Slides...")
            if source_ids:
                print(f"    仅使用源文件: {source_title or source_ids}")
            else:
                print("    使用 notebook 中的所有源文件")

            if instructions:
                print(f"    自定义指令: {instructions}")

            # 转换格式参数
            format_enum = None
            if slide_format:
                if slide_format.lower() == "detailed":
                    format_enum = SlideDeckFormat.DETAILED_DECK
                elif slide_format.lower() == "presenter":
                    format_enum = SlideDeckFormat.PRESENTER_SLIDES

            length_enum = None
            if slide_length:
                if slide_length.lower() == "short":
                    length_enum = SlideDeckLength.SHORT
                elif slide_length.lower() == "default":
                    length_enum = SlideDeckLength.DEFAULT

            try:
                # 生成 Slide Deck（演示文稿）
                status = await client.artifacts.generate_slide_deck(
                    notebook_id,
                    source_ids=source_ids,
                    language=language,
                    instructions=instructions,
                    slide_format=format_enum,
                    slide_length=length_enum,
                )
                print(f"✓ Slides 生成任务已创建 (Task ID: {status.task_id})")

                # 等待生成完成（可能需要2-5分钟）
                print("[2/3] 等待生成完成（可能需要2-5分钟）...")
                await self._wait_with_progress(
                    client,
                    notebook_id,
                    status.task_id,
                    task_name="Slides生成",
                    check_interval=5,
                    max_wait_time=600,  # 最多等10分钟
                )

            except TimeoutError as e:
                print(f"\n✗ {e}")
                print("\n你可以:")
                print(
                    f"1. 稍后在浏览器中查看: https://notebooklm.google.com/notebook/{notebook_id}"
                )
                print(f"2. 稍后手动下载: python3 download_slides.py {notebook_id}")
                raise
            except Exception as e:
                print(f"\n✗ 生成失败: {e}")
                raise

            try:
                # 下载 Slides PDF
                print("[3/3] 正在下载 Slides PDF...")

                # 生成文件名
                if source_title:
                    # Use the source stem. A raw "book.md" title otherwise becomes "bookmd".
                    stem = Path(source_title).stem
                    safe_title = "".join(
                        c
                        for c in stem
                        if c.isalnum() or c in (" ", "-", "_")
                    ).strip()
                else:
                    # 使用 notebook ID
                    safe_title = notebook_id

                output_file = download_path / f"{safe_title or 'slides'}_slides.pdf"

                await client.artifacts.download_slide_deck(
                    notebook_id, str(output_file)
                )
                print(f"✓ 已下载到: {output_file}")

                return str(output_file)

            except Exception as e:
                print(f"\n✗ 下载失败: {e}")
                print("\n你可以手动下载:")
                print(f"  python3 download_slides.py {notebook_id}")
                raise

    async def upload_and_generate_slides(
        self,
        content: str,
        title: str,
        download_dir: str | None = None,
        instructions: str | None = "创建适合儿童和少年阅读的，卡通风格",
        language: str = "en",
        slide_format: str | None = "detailed",
        slide_length: str | None = "default",
    ) -> str:
        """一键上传并生成Slides

        Args:
            content: Markdown格式的绘本内容
            title: 源文件标题
            download_dir: 下载目录
            instructions: 自定义生成指令，默认："创建适合儿童和少年阅读的，卡通风格"
            language: 语言代码，默认 'en'
            slide_format: 格式（'detailed' 或 'presenter'），默认 'detailed'
            slide_length: 长度（'short' 或 'default'），默认 'default'

        Returns:
            下载的Slides文件路径
        """
        # 上传到"儿童绘本" notebook
        notebook_id, source_id, source_title = await self.upload(content, title)

        # 生成并下载（只使用刚上传的源文件）
        slides_path = await self.generate_slides(
            notebook_id,
            [source_id],
            source_title,
            download_dir,
            instructions,
            language,
            slide_format,
            slide_length,
        )

        return slides_path

    async def generate_audio(self, notebook_id: str, instructions: str = "") -> str:
        """生成音频播客

        Args:
            notebook_id: NotebookLM笔记本ID
            instructions: 生成指示（可选）

        Returns:
            任务ID
        """
        self._check_notebooklm()

        async with await NotebookLMClient.from_storage() as client:
            status = await client.artifacts.generate_audio(
                notebook_id, instructions=instructions
            )
            return status.task_id

    async def download_audio(
        self, notebook_id: str, output_path: str
    ) -> str:
        """下载音频播客

        Args:
            notebook_id: NotebookLM笔记本ID
            output_path: 输出文件路径

        Returns:
            下载的文件路径
        """
        self._check_notebooklm()

        async with await NotebookLMClient.from_storage() as client:
            await client.artifacts.download_audio(notebook_id, output_path)
            return output_path
