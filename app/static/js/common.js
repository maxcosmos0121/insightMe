/**
 * InsightMe 通用JavaScript功能
 * 基于jQuery 3.7.1
 */

$(document).ready(function () {
    // 全局初始化
    initCommonFeatures();

    // 表单验证工具
    initFormValidation();

    // 动画效果
    initAnimations();

    // 消息提示系统
    initMessageSystem();
});

/**
 * 通用功能初始化
 */
function initCommonFeatures() {
    // 输入框焦点效果
    $('.form-control, .form-select').on('focus', function () {
        $(this).parent().addClass('focused');
    }).on('blur', function () {
        $(this).parent().removeClass('focused');
    });

    // 回车键提交表单
    $('.form-control').on('keypress', function (e) {
        if (e.which === 13) {
            $(this).closest('form').submit();
        }
    });

    // 自动隐藏提示信息
    setTimeout(function () {
        $('.alert').fadeOut(500);
    }, 5000);
}

/**
 * 表单验证初始化
 */
function initFormValidation() {
    // 实时输入验证
    $('.form-control[required]').on('input', function () {
        validateField($(this));
    });

    // 表单提交验证
    $('form').on('submit', function (e) {
        if (!validateForm($(this))) {
            e.preventDefault();
            return false;
        }

        // 显示加载状态
        var submitBtn = $(this).find('button[type="submit"]');
        if (submitBtn.length) {
            submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span>处理中...');
        }
    });
}

/**
 * 验证单个字段
 */
function validateField($field) {
    var value = $field.val().trim();
    var isValid = true;
    var feedback = $field.next('.invalid-feedback');

    // 清除之前的验证状态
    $field.removeClass('is-invalid is-valid');
    feedback.hide();

    // 必填字段验证
    if ($field.prop('required') && !value) {
        $field.addClass('is-invalid');
        feedback.text('此字段为必填项').show();
        isValid = false;
    }
    // 最小长度验证
    else if ($field.attr('minlength') && value.length < parseInt($field.attr('minlength'))) {
        $field.addClass('is-invalid');
        feedback.text('最少需要' + $field.attr('minlength') + '个字符').show();
        isValid = false;
    }
    // 邮箱验证
    else if ($field.attr('type') === 'email' && value && !isValidEmail(value)) {
        $field.addClass('is-invalid');
        feedback.text('请输入有效的邮箱地址').show();
        isValid = false;
    }
    // 数字验证
    else if ($field.attr('type') === 'number' && value && isNaN(value)) {
        $field.addClass('is-invalid');
        feedback.text('请输入有效的数字').show();
        isValid = false;
    }
    else if (value) {
        $field.addClass('is-valid');
    }

    return isValid;
}

/**
 * 验证整个表单
 */
function validateForm($form) {
    var isValid = true;

    // 验证所有必填字段
    $form.find('.form-control[required]').each(function () {
        if (!validateField($(this))) {
            isValid = false;
        }
    });

    return isValid;
}

/**
 * 邮箱格式验证
 */
function isValidEmail(email) {
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * 动画效果初始化
 */
function initAnimations() {

    // 悬停效果
    $('.btn, .card, .form-section').hover(
        function () {
            $(this).addClass('hover-effect');
        },
        function () {
            $(this).removeClass('hover-effect');
        }
    );

    // 点击动画
    $('.btn').on('click', function () {
        $(this).addClass('clicked');
        setTimeout(function () {
            $('.btn').removeClass('clicked');
        }, 200);
    });
}

/**
 * 消息提示系统初始化
 */
function initMessageSystem() {
    // 自动隐藏消息
    $('.alert').each(function () {
        var $alert = $(this);
        var autoHide = $alert.data('auto-hide') !== false;
        var duration = $alert.data('duration') || 5000;

        if (autoHide) {
            setTimeout(function () {
                $alert.fadeOut(500);
            }, duration);
        }
    });
}

/**
 * 显示消息提示
 */
function showMessage(message, type, duration) {
    type = type || 'info';
    duration = duration || 5000;

    var alertClass = 'alert-' + type;
    var icon = getMessageIcon(type);

    var alertHtml = '<div class="alert ' + alertClass + ' alert-dismissible fade show" role="alert" data-auto-hide="true" data-duration="' + duration + '">' +
        '<i class="' + icon + ' me-2"></i>' +
        message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
        '</div>';

    // 移除现有的消息
    $('.alert').remove();

    // 添加新消息
    $('.page-title').after(alertHtml);

    // 自动隐藏
    setTimeout(function () {
        $('.alert').fadeOut(500);
    }, duration);
}

/**
 * 获取消息图标
 */
function getMessageIcon(type) {
    var icons = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };
    return icons[type] || icons['info'];
}

/**
 * 确认对话框
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        if (typeof callback === 'function') {
            callback();
        }
    }
}

/**
 * 加载状态管理
 */
function showLoading($element, text) {
    text = text || '加载中...';
    $element.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span>' + text);
}

function hideLoading($element, originalText) {
    $element.prop('disabled', false).html(originalText || '提交');
}

/**
 * AJAX请求工具
 */
function ajaxRequest(url, data, options) {
    var defaultOptions = {
        type: 'POST',
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                showMessage(response.message || '操作成功', 'success');
                if (response.redirect) {
                    setTimeout(function () {
                        window.location.href = response.redirect;
                    }, 1000);
                }
            } else {
                showMessage(response.message || '操作失败', 'error');
            }
        },
        error: function () {
            showMessage('网络错误，请稍后重试', 'error');
        }
    };

    $.extend(defaultOptions, options);

    $.ajax({
        url: url,
        data: data,
        type: defaultOptions.type,
        dataType: defaultOptions.dataType,
        success: defaultOptions.success,
        error: defaultOptions.error
    });
}

/**
 * 日期时间格式化
 */
function formatDateTime(dateString) {
    var date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * 数字格式化
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * 防抖函数
 */
function debounce(func, wait) {
    var timeout;
    return function executedFunction() {
        var later = function () {
            clearTimeout(timeout);
            func();
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 */
function throttle(func, limit) {
    var inThrottle;
    return function () {
        var args = arguments;
        var context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(function () {
                inThrottle = false;
            }, limit);
        }
    };
} 