# Honeybee-MCP -- Agent 指南

本文件面向在此代码库中工作的 AI Agent（Cursor、Copilot、OpenCode、Codex 等），提供项目结构、约定和关键技术背景。

---

## 项目定位

Honeybee-MCP 是一个 **MCP (Model Context Protocol) 服务端**，核心职责是将 Ladybug Tools / Honeybee 建筑能耗建模生态的能力暴露为结构化的工具调用。服务端基于 `fastmcp` 构建，运行时维护一个内存中的 Honeybee Model 状态，所有工具围绕这个状态进行读写。

---

## 架构概览

```
server.py                          # 入口，启动 FastMCP
└── tools/
    ├── mcp_context.py              # 全局 FastMCP 实例 (mcp)
    ├── load_model.py               # load_model / load_model_from_dict
    ├── save_model.py               # save_model
    ├── operations/                 # 四条核心总线
    │   ├── add_bus.py              #   add()      -- 创建对象
    │   ├── apply_bus.py            #   apply()    -- 赋值属性
    │   ├── query_bus.py            #   query()    -- 查询属性
    │   └── remove_bus.py           #   remove()   -- 删除对象
    ├── library/bus.py              # search_properties()
    ├── visualization/bus.py        # visualization()
    ├── sync/bus.py                 # 共享内存同步 (Grasshopper)
    ├── versioning/bus.py           # version_control()
    └── state/
        ├── manager.py              # ModelManager -- 全局单例
        ├── hooks.py                # 编辑后自动回写等钩子
        ├── energy_resources.py     # Energy 资源追踪
        ├── radiance_resources.py   # Radiance 资源追踪
        └── summary.py             # 模型摘要生成
```

### 关键设计模式

1. **Bus Pattern（总线模式）**：`add`、`apply`、`query`、`remove` 四个工具各自维护一个注册表（`*_REGISTRY`），将 operation 字符串映射到具体的 service 函数。新增操作只需在注册表中添加一行，无需修改总线代码本身。

2. **State Manager 单例**：`tools/state/manager.py` 中的 `manager` 是全局唯一的模型持有者。所有工具通过 `manager.model` 访问当前模型，通过 `manager.load()` / `manager.load_from_dict()` 加载模型。

3. **资源追踪层**：Energy 和 Radiance 资源（时间表、构造、修改器等）不仅挂在宿主对象上，还被 `state/energy_resources.py` 和 `state/radiance_resources.py` 独立追踪。这保证了序列化时资源不会丢失。

4. **共享内存桥接**：`sync/` 模块通过内存映射文件与 Grasshopper 双向通信。写入时在文件头部用 8 字节小端序记录数据长度，随后是 UTF-8 编码的 JSON。

---

## 开发约定

### 代码风格

- Python 3.10+，无类型注解强制要求，但鼓励在公共 API 上使用。
- 所有 MCP 工具函数通过 `@mcp.tool()` 装饰器注册。
- 工具函数返回 `dict`，必须包含 `"success": bool` 字段。
- 字符串格式化使用 `str.format()`，不使用 f-string（项目既有约定）。

### 新增工具的流程

1. 在对应的 `*_service.py` 中实现业务逻辑函数。
2. 在对应的 `*_bus.py` 的 `*_REGISTRY` 字典中添加映射。
3. 如果涉及新的资源类型，在 `state/` 下的资源追踪模块中添加处理逻辑。
4. 在 `query_bus.py` 的 `QUERY_FIELD_REGISTRY` 中为新类型添加可查询字段。

### 测试

- 测试入口: `test_mcp.py`（集成级烟雾测试）
- 测试目录: `tests/`
- 样本模型: `src/sample/Revit_Sample.hbjson`

### 依赖管理

- 生产依赖: `requirements.txt`（固定版本）
- 开发依赖: `requirements-dev.txt`（浮动版本，跟踪最新兼容版本）

---

## 核心工具速查

| 工具 | 签名 | 说明 |
|------|------|------|
| `load_model` | `(hb_file?, cleanup_irrational?)` | 加载 HBJSON / HBpkl / 共享内存模型 |
| `save_model` | `(name?, folder?, indent?, ...)` | 导出为 HBJSON |
| `query` | `(target_type, identifiers?, fields?, output_mode?, resource_category?)` | 统一查询 |
| `add` | `(operation, target_type, identifiers?, params?)` | 统一创建 |
| `apply` | `(operation, target_type, identifiers?, values?)` | 统一赋值 |
| `remove` | `(operation, identifiers?, options?)` | 统一删除 |
| `search_properties` | `(category, keywords?, vintage?, ...)` | 标准库搜索 |
| `visualization` | `(target_type?, identifiers?, vis_options?, export_formats?, ...)` | 可视化导出 |
| `version_control` | `(action, model_name?, version_id?, ...)` | 版本管理 |
| `load_model_from_shared_memory` | `(name?)` | 从 Grasshopper 共享内存加载 |
| `save_model_to_shared_memory` | `(name?)` | 回写到 Grasshopper 共享内存 |

---

## 重要文件索引

| 路径 | 用途 |
|------|------|
| `server.py` | MCP 服务入口 |
| `tools/__init__.py` | 工具模块汇总注册 |
| `tools/mcp_context.py` | `FastMCP("Honeybee-MCP")` 实例 |
| `tools/state/manager.py` | 全局模型状态管理（单例） |
| `tools/operations/common.py` | `resolve_targets` / `serialize_value` 等共享工具函数 |
| `tools/operations/hvac_config.json` | HVAC 系统类型配置 |
| `src/docs/Resource_Workflows.md` | Energy / Radiance 资源的端到端工作流文档 |
| `grasshopper/src/` | Grasshopper GHPython 组件源码 |

---

## 已知限制

- 服务端为**单用户、单模型**设计，同一时刻只持有一个 Honeybee Model。
- 共享内存桥接仅限本机使用（内存映射文件不跨网络）。
- `visualization` 工具依赖 `ladybug-vtk`，在无头环境下可能需要额外配置。
