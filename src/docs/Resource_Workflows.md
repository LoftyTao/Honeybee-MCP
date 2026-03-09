# Honeybee-MCP 资源工作流示例

本文档用于补充 README 中的总览说明，重点展示两类完整工作流：一类是 `HB-Energy` 资源工作流，另一类是 `HB-Radiance` 资源工作流。这里的“完整”并不是只展示单次 `add` 或 `apply` 调用，而是展示从资源创建、宿主挂接、结果查询、保存、重载验证这一整条闭环。对于 Honeybee-MCP 而言，只有完成这条闭环，对象才算真正进入了可用状态。

本文所有示例默认基线模型为：

`D:\Desktop\Codex\mcp-dev\honeybee-mcp\src\sample\Revit_Sample.hbjson`

---

## 1. Energy：自定义 Occupancy Schedule + People 负荷

这个案例的目标是为某个房间创建一套新的占用时间表（occupancy schedule），将其赋给 `People` 负荷对象，然后验证该资源已经写入模型，并且在保存和重载后仍然存在。这个例子非常适合说明 Honeybee-MCP 中“资源”与“宿主对象”的关系：`ScheduleTypeLimit`、`ScheduleDay`、`ScheduleRuleset` 是资源，`People` 是房间宿主上的负荷对象。

### 步骤 1：加载模型并确认房间标识符

```python
load_model("D:/Desktop/Codex/mcp-dev/honeybee-mcp/src/sample/Revit_Sample.hbjson")

query(
    target_type="room",
    fields=["identifier", "display_name"],
    output_mode="list"
)
```

此时应先选定一个目标房间，例如 `Bath_1_c4ddb28c`。在真实工作中，先查清房间标识符是一条重要原则，因为后续 schedule 本身虽然是资源，但最终必须挂到具体宿主上。

### 步骤 2：创建 `ScheduleTypeLimit`

```python
add(
    operation="schedule_type_limit",
    target_type="model",
    params={
        "identifier": "OfficeFraction",
        "lower_limit": 0,
        "upper_limit": 1,
        "numeric_type": "Continuous",
        "unit_type": "Dimensionless"
    }
)
```

这一步定义的是这个 schedule 的数值边界与类型。对于占用率、照明率或设备率这种 0 到 1 的比例量，`Fraction`（fractional）类的 type limit 是最常见的选择。

### 步骤 3：创建 `ScheduleDay`

```python
add(
    operation="schedule_day",
    target_type="model",
    params={
        "identifier": "OfficeDay",
        "values": [0, 1, 0.2],
        "times": ["00:00", "08:00", "18:00"]
    }
)
```

这里表达的含义是：午夜到上午 8 点为 0，8 点以后切换到 1，18 点以后切换到 0.2。`ScheduleDay` 是 `ScheduleRuleset` 的基础构件，因此它先作为独立资源被创建。

### 步骤 4：创建 `ScheduleRuleset`

```python
add(
    operation="schedule_ruleset",
    target_type="model",
    params={
        "identifier": "OfficeOccupancy",
        "default_day_identifier": "OfficeDay",
        "schedule_type_limit_identifier": "OfficeFraction"
    }
)
```

这一步将前面创建的 `ScheduleDay` 和 `ScheduleTypeLimit` 组装成一个完整可引用的 `ScheduleRuleset`。到这里为止，资源还只是存在于模型的资源层中，并未自动改变任何房间负荷。

### 步骤 5：将 schedule 挂接到房间 `People`

```python
apply(
    operation="people",
    target_type="room",
    identifiers=["Bath_1_c4ddb28c"],
    values={
        "people_per_area": 0.2,
        "occupancy_schedule_identifier": "OfficeOccupancy"
    }
)
```

这一步才是真正把资源与宿主对象联动起来。Honeybee-MCP 内部会将 `OfficeOccupancy` 解析为一个可复用 schedule，并赋给房间级 `People` 对象。

### 步骤 6：验证宿主对象与资源

```python
query(
    target_type="room",
    identifiers=["Bath_1_c4ddb28c"],
    fields=[
        "properties.energy.people.identifier",
        "properties.energy.people.people_per_area",
        "properties.energy.people.occupancy_schedule.identifier"
    ]
)

query(
    target_type="schedule",
    identifiers=["OfficeOccupancy"],
    fields=["identifier", "schedule_kind", "default_day_schedule", "schedule_type_limit"],
    output_mode="list"
)
```

这里有两个验证层次。第一层验证房间宿主对象是否已经引用正确的 schedule；第二层验证 schedule 资源自身是否仍然存在，并且其内部结构保持正确。

### 步骤 7：保存并重载验证

```python
save_model(
    name="energy_schedule_roundtrip",
    folder="D:/Desktop/Codex/mcp-dev/honeybee-mcp/tests/generated_models",
    indent=2
)

load_model("D:/Desktop/Codex/mcp-dev/honeybee-mcp/tests/generated_models/energy_schedule_roundtrip.hbjson")

query(
    target_type="schedule",
    identifiers=["OfficeOccupancy"],
    fields=["identifier", "default_day_schedule", "schedule_type_limit"],
    output_mode="list"
)
```

如果重载后仍能查询到 `OfficeOccupancy`，并且它仍然引用 `OfficeDay` 与 `OfficeFraction`，说明这一套 Energy 资源已经真正进入了 HBJSON 持久化链路。

---

## 2. Energy：自定义围护构造 + Face 赋值

这个案例说明另一条常见路径：并不是所有资源都要先独立创建再挂接。对于自定义 `construction`，当前项目采用的是“在 `apply` 中创建并同时挂接”的策略。

### 步骤 1：先找目标外墙

```python
query(
    target_type="face",
    fields=["identifier", "type", "boundary_condition"],
    output_mode="records"
)
```

选择一个 `Wall + Outdoors` 的面，例如 `Bath_2_9ada4840..Face3`。

### 步骤 2：创建并赋予自定义 opaque construction

```python
apply(
    operation="opaque_attributes",
    target_type="face",
    identifiers=["Bath_2_9ada4840..Face3"],
    values={
        "custom_construction": {
            "identifier": "TestOpaque",
            "materials": [
                {
                    "identifier": "TestMat",
                    "thickness": 0.1,
                    "conductivity": 0.5,
                    "density": 800,
                    "specific_heat": 1000
                }
            ]
        }
    }
)
```

这一步会同时做三件事：创建 `EnergyMaterial`，创建 `OpaqueConstruction`，并将该构造赋给目标 `Face`。由于 Honeybee-MCP 已经把这条路径接到了 HBJSON resource preservation 上，保存时 `materials` 与 `constructions` 都会自动进入 `properties.energy`。

### 步骤 3：验证 `Face` 与资源

```python
query(
    target_type="face",
    identifiers=["Bath_2_9ada4840..Face3"],
    fields=["properties.energy.construction.identifier"]
)

query(
    target_type="energy_resource",
    resource_category="constructions",
    fields=["identifier", "resource_category", "resource_source"],
    output_mode="list"
)
```

---

## 3. Radiance：自定义 Modifier + 外墙赋值

这个案例与前面的 Energy schedule 类似，但对象换成了 Radiance 的 `modifier`。这里的重点在于：`modifier` 既是资源，又是很多宿主对象上的可引用属性。

### 步骤 1：创建自定义 Plastic Modifier

```python
add(
    operation="modifier",
    target_type="model",
    params={
        "identifier": "TestPlastic",
        "modifier_type": "plastic",
        "r_reflectance": 0.5,
        "g_reflectance": 0.5,
        "b_reflectance": 0.5
    }
)
```

### 步骤 2：赋给外墙 Face

```python
apply(
    operation="opaque_attributes",
    target_type="face",
    identifiers=["Bath_2_9ada4840..Face3"],
    values={"modifier_identifiers": ["TestPlastic"]}
)
```

### 步骤 3：验证宿主对象与资源

```python
query(
    target_type="face",
    identifiers=["Bath_2_9ada4840..Face3"],
    fields=["properties.radiance.modifier.identifier"]
)

query(
    target_type="modifier",
    identifiers=["TestPlastic"],
    fields=["identifier", "modifier_type", "resource_source"],
    output_mode="list"
)
```

### 步骤 4：测试安全删除

```python
remove(operation="modifier", identifiers=["TestPlastic"])
```

如果该 modifier 仍被外墙引用，系统应优先返回 `blocked` 信息，而不是直接删除。对于可复用 Radiance 资源，这种“先检查引用，再决定是否删除”的策略非常重要。

---

## 4. Radiance：自定义 ModifierSet + 房间赋值

`ModifierSet` 是房间级 Radiance 资源。与单一 modifier 相比，它的价值在于它能为墙、地、顶、窗、门、shade 等多个类别同时提供一整套可复用规则。

### 步骤 1：先创建一个基础 modifier

```python
add(
    operation="modifier",
    target_type="model",
    params={
        "identifier": "RoomPlastic",
        "modifier_type": "plastic",
        "r_reflectance": 0.45,
        "g_reflectance": 0.45,
        "b_reflectance": 0.45
    }
)
```

### 步骤 2：创建 `ModifierSet`

```python
add(
    operation="modifier_set",
    target_type="model",
    params={
        "identifier": "RoomModifierSet",
        "wall_set": {
            "exterior_modifier": "RoomPlastic",
            "interior_modifier": "RoomPlastic"
        },
        "floor_set": {
            "exterior_modifier": "RoomPlastic",
            "interior_modifier": "RoomPlastic"
        },
        "roof_ceiling_set": {
            "exterior_modifier": "RoomPlastic",
            "interior_modifier": "RoomPlastic"
        },
        "shade_set": {
            "exterior_modifier": "RoomPlastic",
            "interior_modifier": "RoomPlastic"
        }
    }
)
```

### 步骤 3：赋给房间

```python
apply(
    operation="room_attributes",
    target_type="room",
    identifiers=["Bath_1_c4ddb28c"],
    values={"modifier_set_identifier": "RoomModifierSet"}
)
```

### 步骤 4：查询验证

```python
query(
    target_type="room",
    identifiers=["Bath_1_c4ddb28c"],
    fields=["properties.radiance.modifier_set.identifier"]
)

query(
    target_type="modifier_set",
    identifiers=["RoomModifierSet"],
    fields=["identifier", "resource_source"],
    output_mode="list"
)
```

---

## 5. Radiance：创建 SensorGrid 与 View

与 `modifier`、`modifier_set` 不同，`sensor_grid` 和 `view` 更接近分析对象（analysis objects），它们直接挂在 `model.properties.radiance` 上，但同样会进入 HBJSON，并在重载后恢复。

### 创建 `SensorGrid`

```python
add(
    operation="sensor_grid",
    target_type="model",
    params={
        "identifier": "Grid_01",
        "sensors": [
            {"pos": [0, 0, 0.8], "dir": [0, 0, 1]},
            {"pos": [1, 0, 0.8], "dir": [0, 0, 1]}
        ]
    }
)
```

### 创建 `View`

```python
add(
    operation="view",
    target_type="model",
    params={
        "identifier": "View_01",
        "position": [0, 0, 1.6],
        "direction": [1, 0, 0],
        "up_vector": [0, 0, 1]
    }
)
```

### 查询验证

```python
query(
    target_type="sensor_grid",
    fields=["identifier", "sensor_count"],
    output_mode="list"
)

query(
    target_type="view",
    fields=["identifier", "direction", "view_type"],
    output_mode="list"
)
```

### 保存并重载验证

```python
save_model(
    name="radiance_analysis_roundtrip",
    folder="D:/Desktop/Codex/mcp-dev/honeybee-mcp/tests/generated_models",
    indent=2
)

load_model("D:/Desktop/Codex/mcp-dev/honeybee-mcp/tests/generated_models/radiance_analysis_roundtrip.hbjson")

query(target_type="sensor_grid", fields=["identifier"], output_mode="list")
query(target_type="view", fields=["identifier"], output_mode="list")
```

---

## 6. Shared Memory：资源型自动回写

如果模型来自 `Grasshopper shared memory`，并且你在 MCP 中所做的编辑已经进入了可序列化的模型字典，那么这些更改会通过 `post_edit_pipeline` 自动写回共享内存。最典型的例子是：

1. 从共享内存加载模型
2. 创建自定义 Energy schedule
3. 把该 schedule 挂到房间 `People`
4. MCP 自动回写
5. Grasshopper Reader 重新读取更新后的模型

这一点的意义在于：共享内存工作流不再只适用于几何对象，也适用于已经纳入 HBJSON 序列化链路的 Energy/Radiance 资源。

---

## 7. 建议的验证顺序

对于任何新的资源型工作流，建议都按下面这条顺序验证：

1. `query` 当前宿主对象与资源状态
2. `add` 创建资源
3. `apply` 将资源挂到宿主对象
4. `query` 验证宿主对象引用
5. `query` 验证资源自身
6. `save_model`
7. `load_model`
8. 再次 `query`

这条顺序的本质，是把“对象可创建”与“对象可持久化”明确区分开来。对于 Honeybee-MCP 的后续扩展，这仍然是最推荐的 acceptance path，也就是验收路径。
