# Templates 目录结构说明

## 重构后的目录组织

为了更好地管理模板文件，我们将原来的扁平结构重新组织为按功能模块分类的目录结构：

### 📁 auth/ - 用户认证相关
- `login.html` - 用户登录页面
- `register.html` - 用户注册页面  
- `profile.html` - 用户资料页面

### 📁 todo/ - 待办事项相关
- `todos.html` - 待办事项列表页面
- `add_todo.html` - 添加待办事项页面
- `edit_todo.html` - 编辑待办事项页面
- `complete_todo.html` - 完成待办事项页面
- `cancel_todo.html` - 取消待办事项页面

### 📁 checkin/ - 打卡签到相关
- `checkin.html` - 打卡主页面
- `checkin_history.html` - 打卡历史记录页面
- `create_checkin_item.html` - 创建打卡项目页面
- `edit_checkin_item.html` - 编辑打卡项目页面
- `do_checkin.html` - 执行打卡页面

### 📁 diary/ - 日记相关
- `diary.html` - 写日记页面

### 📁 common/ - 通用页面
- `home.html` - 首页
- `history.html` - 历史记录页面

## 重构优势

1. **更好的组织结构** - 按功能模块分类，便于查找和维护
2. **清晰的职责分离** - 每个目录负责特定的功能模块
3. **便于扩展** - 新增功能时可以直接在对应目录下添加模板
4. **团队协作友好** - 不同开发者可以专注于不同的功能模块

## 注意事项

- 所有模板路径已在 `views.py` 中更新
- 静态资源路径保持不变
- 模板继承和包含关系保持不变 