## 项目概述

SISYPHUS 是一款命令行文字侦探游戏。玩家扮演州调查员 Jonah Mercer，回到故乡 Saint Barrow 调查 Wren 一家的谋杀案。游戏以文本叙事驱动，通过命令交互推进剧情，包含多结局分支和隐藏结局机制。

## 技术栈

- **语言**: Python 3.12（纯标准库，无第三方依赖）
- **运行方式**: `python3 sisyphus_game.py` 直接运行
- **测试**: `unittest`，位于 `tests/test_sisyphus_game.py`

## 目录结构

```
/workspace/projects/
├── sisyphus_game.py          # 游戏主文件（1349 行），包含全部游戏逻辑
├── sisyphus_cli_script.md    # 设计文档 / 叙事脚本
├── README.md                 # 项目说明（不含灵感来源作品名）
├── tests/
│   ├── test_sisyphus_game.py # 单元测试（结局判定、命令解析等，15 个）
│   └── test_acceptance.py    # 用户验收测试（全流程模拟，48 个）
├── docs/plans/               # 扩展计划文档
├── .coze                     # 项目配置
└── AGENTS.md                 # 本文件
```

## 关键入口 / 核心模块

- **入口**: `sisyphus_game.py` → `play()` 函数（`if __name__ == "__main__"` 触发）
- **核心数据结构**:
  - `GameState` — 玩家状态（勇气/清晰度/理性、线索、标记等）
  - `Scene` — 场景定义（文本、交互、前置条件）
  - `Interaction` — 可交互动作（效果、一次性标记）
  - `CommandResult` — 命令执行结果
- **核心函数**:
  - `parse_command()` — 解析玩家输入
  - `run_scene_command()` — 场景内命令分发
  - `determine_ending()` — 结局判定逻辑（含隐藏结局）
  - `make_scenes()` — 构建全部场景数据
  - `build_think_text()` — 生成内省文本

## 运行与预览

- **运行**: `python3 sisyphus_game.py`
- **测试**: `cd /workspace/projects && python3 -m unittest discover -s tests -v`（63 个测试：15 单元 + 48 验收）
- **预览**: 不可预览（CLI 交互式游戏，非 Web/小程序/App 类型）
- **部署**: 不适用（纯本地 CLI 工具，无 HTTP 服务）

## 用户偏好与长期约束

- 游戏文本为英文
- 纯标准库实现，不引入第三方依赖

## 常见问题和预防

- 游戏是交互式 CLI，无法通过非交互方式（如 curl）测试主流程
- 单元测试覆盖结局判定和命令解析等纯逻辑部分，新增逻辑应尽量保持可测试性
