# 配置文件说明

> 本文件对应 `.state/config.json`。AI 每次会话启动时读取该 JSON 恢复配置。
> 法律人可直接编辑 `config.json` 填入真实信息，或在对话中说"设置我的律所为XX"由 AI 写入。

## 配置项说明

| 字段 | 含义 | 示例 | 是否必填 |
|------|------|------|----------|
| `lawyer_name` | 法律人姓名（用于文书落款、署名） | 楠哥 | 是 |
| `firm_name` | 律师事务所全称（文书抬头） | XX律师事务所 | 是 |
| `license_no` | 执业证号 | 1110120XXXXXX | 否 |
| `default_court` | 常用管辖法院（默认填入文书"此致"处） | 北京市朝阳区法院 | 否 |
| `feishu_webhook` | 飞书机器人 webhook（集成发送用） | （空=未配置） | 否 |
| `email` | 法律人邮箱（邮件提醒用） | （空=未配置） | 否 |
| `integration_enabled` | 是否启用外部集成（飞书/邮件） | false | 否 |
| `knowledge_base_path` | 知识库路径 | L4_知识库层 | 否 |
| `state_path` | 状态文件路径 | .state | 否 |
| `domains` | 启用/可用业务领域（见 领域配置.md） | active: [医疗损害, 劳动争议, 合同纠纷] | 否 |
| `extensions.modules_registered` | 已注册功能模块（见 模块注册表.md） | [M01..M06] | 否 |
| `mcp_sources.pkulaw` | 北大法宝法律数据库 MCP（外部知识源，**预留**） | enabled: false, status: reserved | 否 |
| `integrations.tencent_ima` | 腾讯 ima 接口（外部客户端/知识同步，**预留**） | enabled: false, status: reserved | 否 |

> V6.1 新增 `mcp_sources` / `integrations` 为**预留扩展字段**，默认 `enabled=false`，不影响现有行为（向后兼容，`schema_version` 仍为 2）。详见 `L0_存储层/集成接口.md`。

## 自动画像完善协议（V6.3）

> 设计原则：**安装即可用，使用中自动完善**。个人化字段不预填、不阻塞；AI 在工作对话中自动识别法律人信息并回写，无需专门询问。

- **自动识别范围**：法律人姓名、律所全称、执业证号、常用管辖法院、邮箱、飞书 webhook
- **触发时机**：对话中出现明确的事实性信息（如"我们恒和信""此致成都市高新区人民法院"）即回写对应字段；同一字段以最新确认为准
- **回写规则**：只回写事实信息，不猜测；识别不确定时保持空白并在文书中用占位符提示
- **灰度边界**：涉及对外发送（webhook/邮箱）的配置变更，回写后须向法律人口头确认一次才启用（留人工决策灰度）

## 使用约定

- **文书落款**：生成起诉状/律师函时，自动从 `firm_name` + `lawyer_name` 填充
- **管辖法院**：生成文书"此致 XX 人民法院"时，优先用案件 meta 中的 court，缺失则回退 `default_court`
- **提醒发送**：`integration_enabled=false` 时，AI 只生成提醒文本输出到对话，不实际发送（见 SKILL.md 集成边界声明）

## 修改方式

- 手动：直接编辑 `config.json`
- 对话："把我的律所改成XX所""设置飞书 webhook 为 xxx"
- AI 写入后即时生效，下次会话自动读取
