# 配置文件说明

> 本文件对应 `.state/config.json`。AI 每次会话启动时读取该 JSON 恢复配置。
> 律师可直接编辑 `config.json` 填入真实信息，或在对话中说"设置我的律所为XX"由 AI 写入。

## 配置项说明

| 字段 | 含义 | 示例 | 是否必填 |
|------|------|------|----------|
| `lawyer_name` | 律师姓名（用于文书落款、署名） | 楠哥 | 是 |
| `firm_name` | 律师事务所全称（文书抬头） | XX律师事务所 | 是 |
| `license_no` | 执业证号 | 1110120XXXXXX | 否 |
| `default_court` | 常用管辖法院（默认填入文书"此致"处） | 北京市朝阳区法院 | 否 |
| `feishu_webhook` | 飞书机器人 webhook（集成发送用） | （空=未配置） | 否 |
| `email` | 律师邮箱（邮件提醒用） | （空=未配置） | 否 |
| `integration_enabled` | 是否启用外部集成（飞书/邮件） | false | 否 |
| `knowledge_base_path` | 知识库路径 | L4_知识库层 | 否 |
| `state_path` | 状态文件路径 | .state | 否 |

## 使用约定

- **文书落款**：生成起诉状/律师函时，自动从 `firm_name` + `lawyer_name` 填充
- **管辖法院**：生成文书"此致 XX 人民法院"时，优先用案件 meta 中的 court，缺失则回退 `default_court`
- **提醒发送**：`integration_enabled=false` 时，AI 只生成提醒文本输出到对话，不实际发送（见 SKILL.md 集成边界声明）

## 修改方式

- 手动：直接编辑 `config.json`
- 对话："把我的律所改成XX所""设置飞书 webhook 为 xxx"
- AI 写入后即时生效，下次会话自动读取
