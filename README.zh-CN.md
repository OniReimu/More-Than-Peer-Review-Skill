# More Than Peer Review

More Than Peer Review 是一个以显式授权、本地处理和证据边界为核心的 Codex
Skill，用于将保密稿件从 Intake 推进到可供人工核验的最终审稿草稿。

它整合了：

- PDF/DOCX 防御性安全预检；
- 研究动机、创新性、claim–mechanism、设计与系统假设审查；
- claim–evidence、方法、统计和可复现性审计；
- 期刊默认四档与会议专用 Rubric；
- `private-review.md` 到自然书写风格 `submission-review.md` 的受控转换；
- 在不改变证据、结论和披露要求的前提下，检查套话开场、等长评论及重复收尾；
- 最终作者与编辑意见正文禁止使用 em dash、分号和冒号；
- 私有分析可以全面，但最终意见围绕一条审稿主线和通常一到两个根本漏洞展开，并写成三到四条相互关联、未必独立的作者意见；
- 当这些漏洞足以支持 recommendation 时停止扩展，次要清单问题保留在私有记录；
- 作者可见与编辑私密渠道分离；
- 用户明确要求时的网页草稿填报。

## 默认不授权

Skill 不会把文件放入目录、调用 Skill、既往授权或之前的审稿视为本次许可。
在读取保密内容前，用户必须明确确认：

- 有权审阅指定材料；
- 控制该稿件的政策允许计划中的本地 AI 辅助；
- 保密、NDA、共同审稿、留存和披露要求已经处理；
- 利益冲突已经评估；
- 最终意见将由负责任的人类审稿人核验。

确认可以覆盖一篇稿件或明确列出的一个批次，但不能自动延伸到未来稿件。

## Research Presentation

本项目不集成、不安装、也不会自动调用 Research Presentation。只有用户明确要求
Explain Why 或研究展示时，才可以将已经冻结且通过安全检查的同一篇稿件材料交给
独立安装的
[`research-presentation`](https://github.com/DELONG-L/Research-Presentation-Skill)。
缺少该外部 Skill 不影响审稿完成。

## 安装

```bash
git clone https://github.com/DELONG-L/More-Than-Peer-Review-Skill.git
cd More-Than-Peer-Review-Skill
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$(pwd)/more-than-peer-review" \
  "${CODEX_HOME:-$HOME/.codex}/skills/more-than-peer-review"
```

重新启动 Codex 或开启一个新任务后，可以使用：

```text
使用 $more-than-peer-review 审核这篇论文，并生成可以提交前人工核验的审稿草稿。
```

## 本地环境

- Python 3.11+
- 推荐安装 `qpdf`、Poppler 和 Tesseract
- DOCX 需要一个符合期刊政策且不会激活宏、链接、模板或嵌入对象的本地 PDF
  渲染路径

防御性预检不是沙箱或恶意软件检测器，`PASS` 也不证明文档绝对安全或不存在提示词
注入。自动检查不能代替同行评审和人工核验。

## 测试

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile more-than-peer-review/scripts/*.py tests/*.py
```

只允许使用合成测试材料。不得提交真实稿件、审稿意见、安全报告、编辑通信、账号
信息或审稿人身份。

## 许可证

MIT。参见 [LICENSE](LICENSE) 和
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
