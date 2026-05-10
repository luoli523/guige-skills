# NotebookLM Notes

`guige-picbook` uploads the generated Markdown book into a NotebookLM notebook, then asks NotebookLM to generate a Slides PDF.

NotebookLM support is mandatory in the self-managed environment by default. The launcher installs `requirements.txt` and `requirements-notebooklm.txt` together. If NotebookLM dependency setup fails, the launcher exits with an error instead of running a partial environment.

Default behavior:

- Notebook name: `儿童绘本`
- Slides instructions: `创建适合儿童和少年阅读的，卡通风格`
- Format: `detailed`
- Length: `default`
- Only the just-uploaded source is used for slide generation.

Useful overrides:

```bash
--nlm-instructions "创建色彩鲜艳、适合小学生课堂展示的卡通风格演示文稿"
--nlm-format presenter
--nlm-length short
```

Failure handling:

- Missing `notebooklm-py`: run `python3.11 skills/guige-picbook/scripts/main.py setup`.
- If your package index cannot resolve `notebooklm-py>=0.3.2`, setup fails by design. Fix the package source or install from the upstream source used by your environment, then rerun setup.
- Missing login: run `notebooklm login`.
- Timeout or download failure: Markdown remains in the local output folder, but the command fails. Rerun `generate-slides` with the NotebookLM URL or ID after fixing the issue.

Use `--no-slides` when the task only needs a Markdown book or when the current environment has no NotebookLM browser login. This skips Slides generation, not NotebookLM dependency setup.
