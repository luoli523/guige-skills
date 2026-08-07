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
source:
  - title: 来源名称
    locator: 篇章、页码或可定位位置
    note: 来源性质与版本说明
reliability: fact | contested | legend | literary | adapted
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

## 二、准入规则

1. 找不到可定位来源时，可以作为灵感便笺保存，但不得标为 `fact`。
2. 争议说法至少记录分歧点；传说与文学形象不得冒充史实。
3. 一条素材至少应提供一个感官细节和一个叙事用途，否则暂不进入正式库。
4. 明确谁有资格知道这件事，防止人物知识越界。
5. 记录年代和地域边界；无法确定时显式写 `unknown`，不要猜成确定事实。

## 三、场景调用

每场最多选择少量高相关素材，并先回答：

- 它由谁看见、说出或使用？
- 它改变了什么行动、判断、关系或风险？
- 删除它以后，场景是否明显变弱？

如果第三问答案是否定的，该素材大概率只是装饰，应删除或改造成情节功能。

## 四、改编标记

为了剧情对素材作有意识的变形时，将 `reliability` 标为 `adapted`，并在 `source.note` 说明真实版本与改编处。这样既保留创作自由，也避免后续把虚构设定误当史实。
