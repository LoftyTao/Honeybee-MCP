# Honeybee-MCP 工具工作流参考

本文档覆盖 Honeybee-MCP 全部工具的使用场景，按照从简单到复杂的顺序组织。每个工作流以自然语言提示词的形式呈现，方便直接作为 AI Agent 的输入参考。文末记录了当前已知的功能异常，用于指导后续修复。

所有示例默认基线模型为项目内置的 `src/sample/Revit_Sample.hbjson`。

---

## 1. 模型加载与保存

模型 I/O 是所有操作的前提。加载模型后才能进行查询、编辑和导出。

### 1.1 从文件加载

```
加载 src/sample/Revit_Sample.hbjson 模型文件。
```

### 1.2 从 Grasshopper 共享内存加载

不指定文件时，服务端自动扫描共享内存中的 Grasshopper 模型。

```
加载模型。
```

如果有多个 Grasshopper 模型，可指定加载最新的：

```
加载最新的 Grasshopper 模型。
```

### 1.3 保存为 HBJSON

```
把模型保存到 output 文件夹，命名为 demo。
```

带格式化缩进：

```
保存模型到 output 文件夹，命名为 formatted_output，缩进 2 个空格。
```

---

## 2. 基础查询

`query` 是使用最频繁的工具，覆盖几何对象、Energy 资源和 Radiance 资源。

### 2.1 模型概况

```
查看当前模型的基本信息：名称、Room 数量、建筑面积。
```

### 2.2 Room 列表

```
列出所有 Room，带上面积和层数。
```

### 2.3 Face 属性

```
查询所有 Face 的类型、边界条件和窗墙比。
```

### 2.4 Aperture 和 Door

```
列出所有 Aperture，显示面积、朝向和所属的 Face。
```

```
列出所有 Door，显示是否为玻璃门。
```

### 2.5 Shade

```
查询所有 Shade，显示面积和是否为室内。
```

### 2.6 按数量统计

仅统计数量而不获取完整数据：

```
统计模型里有多少个 Room、多少个 Face、多少个 Aperture。
```

---

## 3. 标准库搜索

在编辑模型之前，通常需要先从 Honeybee 标准库（ASHRAE、NECB 等）中检索可用的预定义资源。

### 3.1 检索 Construction

```
搜索适用于气候区 5 的外墙 Construction。
```

### 3.2 检索 Construction Set

```
搜索 2019 版本的 Construction Set。
```

### 3.3 检索 Program Type

```
搜索包含 "Office" 关键词的 Program Type。
```

```
搜索适用于公寓的 Program Type，筛选 2019 版本。
```

### 3.4 检索 Modifier

```
搜索包含 "Generic" 关键词的 Modifier。
```

---

## 4. 添加几何子对象

`add` 工具用于在已有的 Face 或 Aperture 上创建新的子对象。

### 4.1 按比例添加 Aperture

最常用的开窗方式，按窗墙比批量操作：

```
给所有外墙 Face 按 0.4 的比例添加 Aperture。
```

### 4.2 按精确尺寸添加 Aperture

```
在 Face "LivingRoom_Wall_South" 上添加一扇 1.5m 宽、2.0m 高的 Aperture。
```

### 4.3 按比例为矩形面添加 Aperture

```
给所有外墙 Face 按 0.6 的比例添加矩形 Aperture。
```

### 4.4 按尺寸为矩形面添加 Aperture

```
给外墙 Face 按 1.2m 宽、1.8m 高的尺寸添加矩形 Aperture。
```

### 4.5 按网格比例添加 Aperture

```
给所有外墙 Face 按 0.4 的比例添加网格化 Aperture。
```

### 4.6 添加 Louver

```
给南向 Aperture 添加 Louver，深度 0.15m。
```

### 4.7 按数量添加 Louver

```
给南向 Aperture 添加 6 片 Louver。
```

### 4.8 按间距添加 Louver

```
给南向 Aperture 按 0.1m 的间距添加 Louver。
```

---

## 5. 删除对象

`remove` 工具支持批量或选择性删除，并对引用关系进行完整性检查。

### 5.1 清除所有 Aperture

```
清除模型中所有 Aperture。
```

### 5.2 清除所有 Door

```
清除模型中所有 Door。
```

### 5.3 清除所有 Shade

```
清除所有 Shade。
```

### 5.4 清除特定 Face 上的子对象

```
清除 Face "Bedroom_1_Wall_East" 上的所有子对象。
```

### 5.5 清除 Room 上的 Shade

```
清除 Room "Bedroom_1" 上的所有 Shade。
```

---

## 6. 赋值基础属性

`apply` 工具将属性和资源挂接到已有对象上。本节覆盖几何对象级别的属性赋值。

### 6.1 Room 属性

为 Room 设置 Program Type、Construction Set 等：

```
给所有卧室 Room 应用 "2019::MidriseApartment::Apartment" Program Type。
```

### 6.2 HVAC 系统

```
为所有卧室应用 PTAC 暖通系统。
```

```
为所有办公室 Room 应用 Ideal Air 系统。
```

### 6.3 不透明面属性

对 Face 设置或创建 Construction：

```
给外墙 Face "Bedroom_1_Wall_South" 应用 "Generic Exterior Wall" Construction。
```

自定义创建 Construction 并同时赋值：

```
给 Face "Bedroom_1_Wall_South" 创建一个自定义的 Opaque Construction，包含一层 0.1m 厚、导热系数 0.5 的材料。
```

### 6.4 窗户属性

```
给 Aperture "Window_South_1" 应用 "Generic Double Pane" Construction。
```

### 6.5 Shade 属性

```
给所有 Shade 设置反射率为 0.5。
```

---

## 7. Energy 资源工作流

Energy 资源（Schedule、负荷对象等）的创建需要按照依赖关系逐步进行：先创建基础资源，再组装成复合资源，最后挂接到宿主对象。

### 7.1 创建 ScheduleTypeLimit

```
创建一个名为 "OfficeFraction" 的 ScheduleTypeLimit，范围 0 到 1，类型 Continuous，单位 Dimensionless。
```

### 7.2 创建 ScheduleDay

```
创建一个名为 "OfficeDay" 的 ScheduleDay：00:00 开始为 0，08:00 切换到 1，18:00 切换到 0.2。
```

### 7.3 创建 ScheduleRuleset

将前面创建的 ScheduleDay 和 ScheduleTypeLimit 组装：

```
创建一个名为 "OfficeOccupancy" 的 ScheduleRuleset，默认日程为 "OfficeDay"，类型限制为 "OfficeFraction"。
```

### 7.4 创建 ScheduleFixedInterval

```
创建一个固定时间间隔的 Schedule，按小时步长提供全年 8760 个值。
```

### 7.5 赋值 People 负荷

将 Schedule 挂接到 Room 的 People 对象：

```
给 Room "Bedroom_1" 设置人员密度为 0.2 人/m²，使用 "OfficeOccupancy" 作为占用时间表。
```

### 7.6 赋值 Lighting 负荷

```
给所有卧室 Room 设置照明功率密度为 10 W/m²。
```

### 7.7 赋值 ElectricEquipment

```
给所有办公室 Room 设置电器设备功率密度为 12 W/m²。
```

### 7.8 赋值 ServiceHotWater

```
给所有卫生间 Room 设置生活热水的流量为 0.1 L/h/m²。
```

### 7.9 赋值 Setpoint

```
给所有卧室 Room 设置制冷温度 26°C、制热温度 20°C。
```

### 7.10 赋值 Ventilation

```
给所有卧室 Room 设置新风量为 0.006 m³/s/人。
```

### 7.11 添加 ProcessLoad

```
给 Room "Kitchen_1" 添加一个 ProcessLoad，功率 500W。
```

### 7.12 删除 ProcessLoad

```
删除 Room "Kitchen_1" 上的所有 ProcessLoad。
```

### 7.13 修改已有 Schedule

```
修改 ScheduleDay "OfficeDay" 的值，将 18:00 后的值改为 0.5。
```

### 7.14 删除 Schedule 资源

```
删除 Schedule "OfficeOccupancy"。
```

> 如果该 Schedule 仍被某个 Room 的负荷对象引用，系统应返回 blocked 提示。

### 7.15 查询 Energy 资源

```
列出所有 Energy 资源，按类别分组。
```

```
查询 Schedule "OfficeOccupancy" 的详细信息：类型、默认日程、关联的 ScheduleTypeLimit。
```

### 7.16 Energy 资源闭环验证

完整的创建-挂接-保存-重载验证：

```
创建 ScheduleTypeLimit "TestFraction"（0-1, Continuous）。
创建 ScheduleDay "TestDay"（00:00=0, 08:00=1, 18:00=0）。
创建 ScheduleRuleset "TestSchedule"，引用上面两个资源。
给 Room "Bedroom_1" 设置 People 负荷，使用 "TestSchedule" 作为占用时间表。
保存模型到 output 文件夹，名称为 "energy_roundtrip"。
重新加载刚保存的模型。
查询 Schedule "TestSchedule" 是否仍然存在且引用完整。
```

---

## 8. Radiance 资源工作流

Radiance 资源包括 Modifier、ModifierSet、SensorGrid 和 View。与 Energy 资源类似，它们也需要先创建再挂接。

### 8.1 创建 Modifier

```
创建一个名为 "WallPlastic" 的 Plastic Modifier，RGB 反射率均为 0.5。
```

### 8.2 将 Modifier 赋给 Face

```
给外墙 Face "Bedroom_1_Wall_South" 赋值 Modifier "WallPlastic"。
```

### 8.3 创建 ModifierSet

ModifierSet 为 Room 级别的多类别 Modifier 集合：

```
创建一个名为 "RoomModSet" 的 ModifierSet，Wall/Floor/RoofCeiling 的内外 Modifier 都设为 "WallPlastic"。
```

### 8.4 将 ModifierSet 赋给 Room

```
给 Room "Bedroom_1" 赋值 ModifierSet "RoomModSet"。
```

### 8.5 创建 SensorGrid

```
创建一个名为 "Grid_01" 的 SensorGrid，传感器点位为 (0,0,0.8) 和 (1,0,0.8)，方向均朝上。
```

### 8.6 创建 View

```
创建一个名为 "View_01" 的 View，位置 (0,0,1.6)，朝向 (1,0,0)，上方向 (0,0,1)。
```

### 8.7 修改已有 SensorGrid

```
修改 SensorGrid "Grid_01"，添加新的传感器点位 (2,0,0.8)。
```

### 8.8 修改已有 View

```
修改 View "View_01"，将朝向改为 (0,1,0)。
```

### 8.9 删除 Modifier（引用检查）

```
删除 Modifier "WallPlastic"。
```

> 如果 "WallPlastic" 仍被 Face 或 ModifierSet 引用，系统应返回 blocked 提示而非直接删除。

### 8.10 删除 SensorGrid / View

```
删除 SensorGrid "Grid_01"。
```

```
删除 View "View_01"。
```

### 8.11 查询 Radiance 资源

```
列出所有 Modifier，显示类型和来源。
```

```
查询 ModifierSet "RoomModSet" 的详细信息。
```

```
列出所有 SensorGrid，显示传感器数量。
```

```
列出所有 View，显示位置和朝向。
```

### 8.12 Radiance 资源闭环验证

```
创建 Modifier "TestPlastic"（plastic, RGB 反射率 0.45）。
创建 ModifierSet "TestModSet"，墙面内外都用 "TestPlastic"。
给 Room "Bedroom_1" 赋值 ModifierSet "TestModSet"。
创建 SensorGrid "TestGrid"，传感器点 (0,0,0.8) 朝上。
创建 View "TestView"，位置 (0,0,1.6) 朝 (1,0,0)。
保存模型到 output 文件夹，名称为 "radiance_roundtrip"。
重新加载刚保存的模型。
查询 Modifier "TestPlastic"、SensorGrid "TestGrid"、View "TestView" 是否仍然存在。
```

---

## 9. 可视化

`visualization` 工具将模型或选中对象导出为 VisualizationSet 和可选的文件格式。

### 9.1 导出整个模型

```
将整个模型导出为可视化文件，保存到 output 文件夹。
```

### 9.2 导出为 VTK

```
把模型导出为 VTK 格式，保存到 output 文件夹。
```

### 9.3 导出为 SVG

```
把模型导出为 SVG 格式。
```

### 9.4 导出选定对象

```
仅把卧室 Room 导出为可视化文件。
```

---

## 10. 版本控制

`version_control` 提供编辑历史管理，支持手动存档和自动快照。

### 10.1 保存版本

```
保存当前模型的一个版本快照，备注 "开窗前的状态"。
```

### 10.2 列出版本历史

```
列出当前模型的所有版本。
```

### 10.3 加载历史版本

```
加载模型 "Revit_Sample" 的版本 v2。
```

### 10.4 撤销和重做

```
撤销上一步操作。
```

```
重做刚才撤销的操作。
```

### 10.5 版本对比

```
对比模型 "Revit_Sample" 的版本 v1 和 v3，看看改了什么。
```

### 10.6 删除版本

```
删除模型 "Revit_Sample" 的版本 v1。
```

### 10.7 清空版本历史

```
清空模型 "Revit_Sample" 的所有版本历史。
```

---

## 11. Grasshopper 共享内存

共享内存桥接用于 Rhino/Grasshopper 与 MCP 服务端之间的实时双向通信。

### 11.1 检查共享内存状态

```
检查共享内存中是否有模型。
```

### 11.2 从共享内存加载

```
从 Grasshopper 共享内存加载模型。
```

### 11.3 编辑后回写

```
把当前模型写回 Grasshopper 共享内存。
```

### 11.4 清除共享内存

```
清除共享内存中的模型数据。
```

### 11.5 清理缓存

```
清理共享内存的过期缓存文件。
```

---

## 12. 复合工作流

以下是跨越多个工具模块的端到端场景，AI Agent 需要自主规划调用顺序。

### 12.1 住宅卧室完整建模

```
加载 src/sample/Revit_Sample.hbjson 模型。
查询所有 Room，识别出卧室。
清除所有 Aperture 和 Door。
搜索公寓类的 Program Type，为所有卧室应用。
按比例给卧室外墙添加 Aperture：南 0.75、西 0.5、东 0.35、北 0.25。
注意：只对外墙 Face 操作。
给南向 Aperture 加上 Louver，参数你定。
为所有卧室应用 PTAC 暖通系统。
保存到 output 文件夹，命名为 demo。
```

### 12.2 自定义 Energy Schedule 全流程

```
加载 src/sample/Revit_Sample.hbjson。
查询 Room 列表，选一个卧室。
创建 ScheduleTypeLimit "MyFraction"（0-1, Continuous, Dimensionless）。
创建 ScheduleDay "MyDay"（00:00=0, 08:00=1, 18:00=0.2）。
创建 ScheduleRuleset "MyOccupancy"，引用以上资源。
给选定的卧室 Room 设置 People 负荷 0.2 人/m²，使用 "MyOccupancy"。
查询该 Room 的 People 属性，确认 Schedule 挂接正确。
保存模型到 output 文件夹，命名为 "schedule_test"。
重新加载 "schedule_test.hbjson"，查询 Schedule "MyOccupancy" 是否仍然存在。
```

### 12.3 Radiance 分析准备

```
加载 src/sample/Revit_Sample.hbjson。
创建 Modifier "AnalysisPlastic"（plastic, RGB 反射率 0.5）。
创建 ModifierSet "AnalysisModSet"，墙/地/顶都用 "AnalysisPlastic"。
给所有 Room 赋值 ModifierSet "AnalysisModSet"。
在每个卧室中心位置创建 SensorGrid，高度 0.8m，朝上。
创建一个 View，从模型正南方看向模型中心。
保存模型。
```

### 12.4 编辑 + 版本控制 + 回滚

```
加载 src/sample/Revit_Sample.hbjson。
保存一个版本快照，备注 "原始状态"。
清除所有 Aperture。
给所有外墙按 0.6 比例添加 Aperture。
保存一个版本快照，备注 "大窗方案"。
撤销到 "原始状态"。
给所有外墙按 0.2 比例添加 Aperture。
保存一个版本快照，备注 "小窗方案"。
对比 "大窗方案" 和 "小窗方案" 的差异。
```

### 12.5 Grasshopper 协作全流程

```
从 Grasshopper 共享内存加载模型。
查询所有 Room 和 Face 的基本信息。
给所有外墙按 0.4 比例添加 Aperture。
为所有 Room 应用 Ideal Air 系统。
把编辑后的模型写回共享内存。
```

---

## 13. 已知问题与功能异常

以下问题基于自动化测试（17 个场景，16 通过 / 1 失败）以及代码审查发现，记录于此以指导后续修复。

### 13.1 自动化测试覆盖范围

测试基于 `tests/mcp_scenario_suite.py`，覆盖以下功能模块：

| 模块 | 覆盖场景 | 结果 |
|------|----------|------|
| `load_model` | 文件加载、字典加载 | 通过 |
| `save_model` | HBJSON 导出 | 通过 |
| `query` | model / room / face / aperture / shade 查询 | 通过 |
| `search_properties` | ProgramType / ConstructionSet / Construction / Modifier 检索 | 通过 |
| `add` (aperture) | `aperture_by_width_height` / `apertures_by_ratio` / `apertures_by_ratio_rectangle` / `apertures_by_ratio_gridded` / `apertures_by_width_height_rectangle` | 通过 |
| `add` (louver) | `louvers` / `louvers_by_count` / `louvers_by_distance_between` | 通过 |
| `apply` (room) | `room_attributes` / `hvac` | 通过 |
| `apply` (construction) | `window_attributes` | 通过 |
| `apply` (shade) | `shade_attributes` | **失败** |
| `remove` | `face_objects` / `all_apertures` / `all_doors` / `all_shades` / `room_shades` | 通过 |
| `version_control` | save / list / info / compare / undo / redo / load / delete / clear | 通过 |

### 13.2 已确认的 Bug

以下问题已在测试中复现，需要修复。

| 编号 | 模块 | 描述 | 错误信息 | 优先级 |
|------|------|------|----------|--------|
| B-01 | `apply` > `shade_attributes` | 给 Shade 批量赋 Modifier 时抛出异常。测试场景：先通过 `add` (louvers) 生成 Shade，再用 `apply` (shade_attributes) 赋 Modifier，在 `apply` 内部触发 TypeError | `TypeError: unhashable type: 'dict'` | 高 |

### 13.3 未覆盖的功能（待后续测试）

以下功能未被当前自动化测试覆盖，需要手动验证或补充测试用例。

| 编号 | 模块 | 描述 | 状态 |
|------|------|------|------|
| U-01 | `add` | `schedule_type_limit` / `schedule_day` / `schedule_ruleset` / `schedule_fixed_interval` 创建流程 | 未测试 |
| U-02 | `add` | `modifier` / `modifier_set` 创建流程 | 未测试 |
| U-03 | `add` | `sensor_grid` / `view` 创建流程 | 未测试 |
| U-04 | `apply` | `people` / `lighting` / `electric_equipment` / `service_hot_water` / `setpoint` / `ventilation` / `process_load` 负荷赋值 | 未测试 |
| U-05 | `apply` | `opaque_attributes`（自定义 Construction 创建并赋值） | 未测试 |
| U-06 | `apply` | `modifier` / `modifier_set` 赋值流程 | 未测试 |
| U-07 | `remove` | `schedule` / `schedule_day` / `schedule_type_limit` / `modifier` / `modifier_set` / `sensor_grid` / `view` / `process_loads` 删除及引用检查 | 未测试 |
| U-08 | `visualization` | VTK / SVG 导出 | 未测试 |
| U-09 | `sync` | 共享内存全部操作（需 Grasshopper 环境） | 未测试 |

### 13.4 设计限制

| 编号 | 描述 |
|------|------|
| L-01 | 服务端为单用户、单模型设计，同一时刻只持有一个 Honeybee Model |
| L-02 | 共享内存桥接仅限本机使用，内存映射文件不支持跨网络 |
| L-03 | `load_model_from_dict` 不触发自动共享内存回写，需手动调用 `save_model_to_shared_memory` |
