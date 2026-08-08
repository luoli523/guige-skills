# 文化素材库规范

本文件规定文化 reference 的保存方式。写法原则见 `culture-weaving.md`。

## 一、单条素材结构

```yaml
id: 唯一且稳定的 kebab-case 标识
category: history | poetry | legend | ritual | region | food | craft | medicine | religion | law
name: 素材名称
period: 适用年代或年代范围
region: 地域范围
social_group: 主要使用或知晓该素材的人群
status: candidate | verified | adopted | rejected
source:
  - title: 来源名称
    locator: 篇章、页码或可定位位置
    note: 来源性质与版本说明
reliability: fact | contested | legend | literary | adapted | invented
literal_meaning: 字面事实或基本内容
cultural_meaning: 当时人可能赋予它的社会与情感含义
sensory_details:
  - 可被人物直接感知的形、声、色、味、触感或气味
social_rules:
  - 与身份、礼法、禁忌、次序或利益相关的规则
possible_conflicts:
  - 能由该素材自然引出的误会、风险、争夺或选择
suitable_characters:
  - 哪类人物会自然知道、使用或误读它
narrative_uses:
  - characterization
  - conflict
  - clue
  - atmosphere
  - worldbuilding
  - theme
misuse_risks:
  - 年代错置、地域错置、身份越界或现代观念投射等风险
```

`status` 表示项目采用流程，`reliability` 表示内容性质，两者不能混用。例如一则地方传说可以经过来源核验后成为 `status: verified`、`reliability: legend`，但仍不能写成历史事实。

## 二、准入规则

1. 找不到可定位来源时，可以作为灵感便笺保存，但不得标为 `fact`。
2. 争议说法至少记录分歧点；传说与文学形象不得冒充史实。
3. 一条素材至少应提供一个感官细节和一个叙事用途，否则暂不进入正式库。
4. 明确谁有资格知道这件事，防止人物知识越界。
5. 记录年代和地域边界；无法确定时显式写 `unknown`，不要猜成确定事实。

## 三、开放式素材流程

素材库不是白名单。模型可以调用已有知识提出库外候选，但必须依次处理：

```text
模型知识、用户记忆或搜索线索
→ candidate：允许发散，不视为作品事实
→ verified：来源、年代、地域与适用人群已经核对
→ adopted：用户确认进入具体作品
→ 写入项目 reference-manifest
```

- 仅凭模型记忆提出的具体史实默认是 `candidate`，并显式标记待核验。
- 构思阶段允许比较库内材料与库外候选，不因已有素材而停止发散。
- 正式设定和正文优先使用 `verified` 或 `adopted` 材料；无法核验又确需使用时，标记为 `adapted` 或 `invented`。
- `invented` 不需要伪造来源，可以在用户确认且通过时代、地域和世界规则检查后从 `candidate` 直接进入 `adopted`；`adapted` 应记录真实材料与改动边界。
- `rejected` 保留简短否决原因，避免以后重复采用同一时代错置或来源误读。
- 项目完整卡片保存在 `materials/`，只有实际采用的条目进入 `reference-manifest.md`。

## 四、场景调用

每场最多选择少量高相关素材，并先回答：

- 它由谁看见、说出或使用？
- 它改变了什么行动、判断、关系或风险？
- 删除它以后，场景是否明显变弱？

如果第三问答案是否定的，该素材大概率只是装饰，应删除或改造成情节功能。

## 五、改编标记

为了剧情对素材作有意识的变形时，将 `reliability` 标为 `adapted`，并在 `source.note` 说明真实版本与改编处。这样既保留创作自由，也避免后续把虚构设定误当史实。
