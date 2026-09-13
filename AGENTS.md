# AGENTS.md

## Knowledge

スキル群の横断的な法則と Agent Skills プラットフォームの仕様を [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) の knowledge bundle にまとめてあります。入口は [knowledge/index.md](knowledge/index.md)。

- description や frontmatter を書くときは [スキル執筆の規約](knowledge/this-repo/skill-authoring-conventions.md)
- 新しいスキルの構成を決めるときは [スキル設計の思想](knowledge/this-repo/skill-design-philosophy.md)
- PR・Issue・タグなど外向きの操作を扱うスキルを書くときは [外向き操作の安全則](knowledge/this-repo/external-action-safety.md)
- SKILL.md の仕様上の制限を確認するときは [Skill フォーマットと段階的開示](knowledge/agent-skills/skill-format-and-loading.md)

検証は `uv run scripts/validate_skills.py`。
