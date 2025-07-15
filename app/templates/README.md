# InsightMe 模板文件说明

## jQuery 集成

本项目已集成 jQuery 3.7.1，所有JavaScript功能都基于jQuery实现。

### 文件结构

```
app/
├── static/
│   ├── js/
│   │   ├── jquery-3.7.1.min.js    # jQuery库文件
│   │   └── common.js              # 通用JavaScript功能
│   └── css/
│       └── common.css             # 通用样式文件
└── templates/
    ├── common/
    │   ├── base.html              # 基础模板（包含jQuery引用）
    │   ├── home.html              # 首页
    │   └── history.html           # 历史页面
    ├── auth/
    │   ├── login.html             # 登录页面（使用jQuery）
    │   ├── register.html          # 注册页面（使用jQuery）
    │   └── profile.html           # 个人资料页面
    ├── todo/
    │   ├── todos.html             # 计划列表
    │   ├── add_todo.html          # 添加计划（使用jQuery）
    │   ├── edit_todo.html         # 编辑计划（使用jQuery）
    │   ├── complete_todo.html     # 完成计划
    │   └── cancel_todo.html       # 取消计划
    ├── checkin/
    │   ├── checkin.html           # 打卡主页
    │   ├── do_checkin.html        # 执行打卡（使用jQuery）
    │   ├── create_checkin_item.html # 创建打卡项目（使用jQuery）
    │   ├── edit_checkin_item.html # 编辑打卡项目（使用jQuery）
    │   └── checkin_history.html   # 打卡历史
    └── diary/
        └── diary.html             # 日记页面
```

### jQuery 功能特性

#### 1. 表单验证
- 实时输入验证
- 提交前验证
- 自定义验证规则
- 错误提示显示

#### 2. 交互效果
- 悬停动画
- 点击反馈
- 页面加载动画
- 平滑过渡效果

#### 3. 消息提示系统
- 成功/错误/警告消息
- 自动隐藏
- 可关闭的消息框
- 动画效果

#### 4. 通用工具函数
- AJAX请求封装
- 日期时间格式化
- 数字格式化
- 防抖和节流函数

### 使用方法

#### 1. 在模板中引入jQuery

```html
<!-- 在页面底部添加 -->
<script src="{{ url_for('static', filename='js/jquery-3.7.1.min.js') }}"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script src="{{ url_for('static', filename='js/common.js') }}"></script>
```

#### 2. 表单验证示例

```html
<form id="my-form">
    <input type="text" class="form-control" name="username" required minlength="3">
    <div class="invalid-feedback"></div>
    <button type="submit">提交</button>
</form>

<script>
$(document).ready(function() {
    // 表单会自动进行验证
    $('#my-form').on('submit', function(e) {
        // 自定义验证逻辑
        if (!validateForm($(this))) {
            e.preventDefault();
            return false;
        }
    });
});
</script>
```

#### 3. 消息提示示例

```javascript
// 显示成功消息
showMessage('操作成功！', 'success');

// 显示错误消息
showMessage('操作失败！', 'error');

// 显示警告消息
showMessage('请注意！', 'warning');
```

#### 4. AJAX请求示例

```javascript
// 发送POST请求
ajaxRequest('/api/submit', {
    data: formData
}, {
    success: function(response) {
        // 自定义成功处理
    }
});
```

#### 5. 动画效果示例

```javascript
// 淡入效果
$('.element').fadeIn(500);

// 滑动效果
$('.element').slideDown(300);

// 自定义动画
$('.element').animate({
    opacity: 0.5,
    left: '+=50'
}, 1000);
```

### 已更新的页面

以下页面已完全使用jQuery重写：

#### 认证相关
- ✅ `login.html` - 登录页面
- ✅ `register.html` - 注册页面

#### 计划管理
- ✅ `add_todo.html` - 添加计划
- ✅ `edit_todo.html` - 编辑计划

#### 打卡功能
- ✅ `do_checkin.html` - 执行打卡
- ✅ `create_checkin_item.html` - 创建打卡项目
- ✅ `edit_checkin_item.html` - 编辑打卡项目

### 主要改进

1. **更好的用户体验**
   - 实时表单验证
   - 平滑的动画效果
   - 即时的用户反馈

2. **代码质量提升**
   - 统一的代码风格
   - 可复用的函数
   - 更好的错误处理

3. **性能优化**
   - 事件委托
   - 防抖和节流
   - 优化的DOM操作

4. **维护性增强**
   - 模块化的代码结构
   - 清晰的函数命名
   - 完善的注释

### 注意事项

1. 确保jQuery在所有自定义脚本之前加载
2. 使用`$(document).ready()`确保DOM加载完成
3. 优先使用jQuery的方法而不是原生JavaScript
4. 利用通用函数减少重复代码

### 未来计划

- [ ] 添加更多动画效果
- [ ] 实现实时数据更新
- [ ] 添加更多交互组件
- [ ] 优化移动端体验 
