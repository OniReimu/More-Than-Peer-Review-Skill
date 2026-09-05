# More Than Peer Review

More Than Peer Review 是一个在本地处理 PDF 或 DOCX 稿件的 Codex 审稿 Skill。

私有分析可以完整检查论文，但最终意见不会追求面面俱到。它先确定一条审稿主线，
再选择通常一到两个决定性的研究动机、系统设计、算法、假设或 claim mechanism
问题，并由这些根本问题展开至少三条、通常四条相互关联的意见。各点不要求彼此
独立，同一原因的不同后果可以分别追问。

写作阶段允许审稿人用第一人称构造攻击或反例，允许主评论明显长于后续评论，也
允许直接以问题收尾。最终正文只使用 Section、Figure 或 Table 定位，不使用页码
或行号，也不使用 em dash、分号和冒号。

项目包含本地文档预检、独立工作区初始化、claim-evidence 检查、统计与可复现性
审查、草稿骨架和最终格式校验工具。工具不会调用网络或模型服务。

读取保密内容前，用户需简要确认有权处理指定稿件，且期刊允许计划中的本地 AI
辅助。这不是 Intake 表单。用户负责处理安全警告、核验最终意见，并遵守期刊的
披露要求。

## 安装

```bash
git clone https://github.com/DELONG-L/More-Than-Peer-Review-Skill.git
cd More-Than-Peer-Review-Skill
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$(pwd)/more-than-peer-review" \
  "${CODEX_HOME:-$HOME/.codex}/skills/more-than-peer-review"
```

## 测试

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile more-than-peer-review/scripts/*.py tests/*.py
```

测试只使用合成材料。不得提交真实稿件、审稿文本、账号信息或审稿人身份。

## 许可证

MIT。参见 [LICENSE](LICENSE) 和 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
