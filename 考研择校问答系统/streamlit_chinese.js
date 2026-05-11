// Streamlit 界面中文化脚本
// 这个脚本会将Streamlit默认的英文界面元素替换成中文

(function() {
    'use strict';

    // 翻译字典
    const translations = {
        // 右上角菜单
        'Deploy this app': '部署此应用',
        'Settings': '设置',
        'Print': '打印',
        'Record a screencast': '录制屏幕',
        'About': '关于',
        'Documentation': '文档',
        'Ask a question': '提问',
        'Report a bug': '报告问题',
        'Streamlit': 'Streamlit框架',

        // 设置面板
        'Settings': '设置',
        'Close': '关闭',
        'Theme': '主题',
        'Use default colors': '使用默认颜色',
        'Custom theme': '自定义主题',
        'Light theme': '浅色主题',
        'Dark theme': '深色主题',
        'Menu and toolbar visibility': '菜单和工具栏可见性',
        // ...
    };

    // 观察DOM变化，动态翻译新添加的元素
    function translateText(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            const text = node.textContent.trim();
            if (translations[text]) {
                node.textContent = node.textContent.replace(text, translations[text]);
            }
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            // 遍历所有子节点
            node.childNodes.forEach(child => translateText(child));
        }
    }

    // 创建观察者
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                translateText(node);
            });
        });
    });

    // 开始观察
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // 初始翻译
    translateText(document.body);

    console.log('Streamlit 中文化脚本已加载');
})();
