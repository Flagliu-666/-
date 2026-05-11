const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'Graduate School Assistant';
pres.title = '考研择校智能问答系统';
pres.subject = '项目介绍与总结';

// Color palette - Ocean Gradient theme
const COLORS = {
  darkBg: '065A82',      // Deep blue - main background
  mediumBg: '1C7293',    // Teal - secondary
  accent: '00A896',      // Mint accent
  white: 'FFFFFF',
  lightGray: 'F0F4F8',
  darkText: '1E3A5F',
  mutedText: '64748B'
};

// Helper for fresh shadow objects
const makeShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.15 });

// ==================== SLIDE 1: Title ====================
let slide1 = pres.addSlide();
slide1.background = { color: COLORS.darkBg };

// Decorative circle
slide1.addShape(pres.shapes.OVAL, {
  x: 7.5, y: -1, w: 4, h: 4,
  fill: { color: COLORS.mediumBg, transparency: 50 }
});
slide1.addShape(pres.shapes.OVAL, {
  x: 8.5, y: 3.5, w: 3, h: 3,
  fill: { color: COLORS.accent, transparency: 60 }
});

// Main title
slide1.addText("考研择校智能问答系统", {
  x: 0.5, y: 1.8, w: 7, h: 1.2,
  fontSize: 44, fontFace: "Microsoft YaHei", bold: true,
  color: COLORS.white, align: "left"
});

// Subtitle
slide1.addText("Graduate School Smart Q&A System", {
  x: 0.5, y: 3.0, w: 7, h: 0.6,
  fontSize: 20, fontFace: "Arial",
  color: COLORS.accent, align: "left"
});

// Tagline
slide1.addText("基于本地数据的智能考研咨询助手", {
  x: 0.5, y: 3.8, w: 6, h: 0.5,
  fontSize: 16, fontFace: "Microsoft YaHei",
  color: COLORS.white, align: "left"
});

// Bottom info bar
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.0, w: 10, h: 0.625,
  fill: { color: "000000", transparency: 30 }
});
slide1.addText("离线可用 | 智能推荐 | 实时查询", {
  x: 0.5, y: 5.1, w: 9, h: 0.4,
  fontSize: 14, fontFace: "Microsoft YaHei",
  color: COLORS.white, align: "center"
});

// ==================== SLIDE 2: Project Overview ====================
let slide2 = pres.addSlide();
slide2.background = { color: COLORS.lightGray };

// Header bar
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.darkBg }
});
slide2.addText("项目概述", {
  x: 0.5, y: 0.2, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei", bold: true,
  color: COLORS.white, margin: 0
});

// Content cards - 2x2 grid
const overviewCards = [
  { title: "项目背景", content: "考研竞争日益激烈，考生需要智能化的择校工具来辅助决策" },
  { title: "核心功能", content: "院校推荐、分数线查询、学科评估、备考指导、政策解读" },
  { title: "技术特点", content: "纯本地运行，无需联网，保护隐私，数据驱动决策" },
  { title: "目标用户", content: "考研学子、家长、培训机构、教育咨询从业者" }
];

overviewCards.forEach((card, i) => {
  const x = 0.5 + (i % 2) * 4.6;
  const y = 1.2 + Math.floor(i / 2) * 2.1;
  
  // Card background
  slide2.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 4.3, h: 1.9,
    fill: { color: COLORS.white },
    shadow: makeShadow()
  });
  
  // Left accent bar
  slide2.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 0.08, h: 1.9,
    fill: { color: COLORS.accent }
  });
  
  // Title
  slide2.addText(card.title, {
    x: x + 0.25, y: y + 0.15, w: 3.8, h: 0.4,
    fontSize: 18, fontFace: "Microsoft YaHei", bold: true,
    color: COLORS.darkText, margin: 0
  });
  
  // Content
  slide2.addText(card.content, {
    x: x + 0.25, y: y + 0.6, w: 3.8, h: 1.1,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: COLORS.mutedText, margin: 0
  });
});

// ==================== SLIDE 3: System Architecture ====================
let slide3 = pres.addSlide();
slide3.background = { color: COLORS.lightGray };

// Header
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.darkBg }
});
slide3.addText("系统架构", {
  x: 0.5, y: 0.2, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei", bold: true,
  color: COLORS.white, margin: 0
});

// Architecture layers
const layers = [
  { name: "应用层", items: ["Web界面 (Streamlit)", "命令行工具 (CLI)", "API接口"], color: COLORS.accent },
  { name: "业务层", items: ["问答引擎", "推荐算法", "规则匹配"], color: COLORS.mediumBg },
  { name: "数据层", items: ["院校数据库", "问答知识库", "分数线数据"], color: COLORS.darkBg }
];

layers.forEach((layer, i) => {
  const y = 1.2 + i * 1.4;
  
  // Layer box
  slide3.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: y, w: 9, h: 1.2,
    fill: { color: layer.color },
    shadow: makeShadow()
  });
  
  // Layer name
  slide3.addText(layer.name, {
    x: 0.7, y: y + 0.15, w: 1.5, h: 0.9,
    fontSize: 20, fontFace: "Microsoft YaHei", bold: true,
    color: COLORS.white, valign: "middle", margin: 0
  });
  
  // Items
  slide3.addText(layer.items.join("  |  "), {
    x: 2.5, y: y + 0.15, w: 6.8, h: 0.9,
    fontSize: 16, fontFace: "Microsoft YaHei",
    color: COLORS.white, valign: "middle", margin: 0
  });
});

// Arrows between layers
for (let i = 0; i < 2; i++) {
  slide3.addText("▼", {
    x: 4.7, y: 2.35 + i * 1.4, w: 0.6, h: 0.3,
    fontSize: 16, color: COLORS.mutedText, align: "center", margin: 0
  });
}

// ==================== SLIDE 4: Core Features ====================
let slide4 = pres.addSlide();
slide4.background = { color: COLORS.lightGray };

// Header
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.darkBg }
});
slide4.addText("核心功能", {
  x: 0.5, y: 0.2, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei", bold: true,
  color: COLORS.white, margin: 0
});

// Feature cards - 3 columns
const features = [
  { title: "智能择校", desc: "根据分数、背景智能推荐最适合的院校" },
  { title: "分数查询", desc: "历年国家线、自划线院校分数线" },
  { title: "学科评估", desc: "教育部学科评估结果与排名" },
  { title: "备考指导", desc: "各科目复习计划与资料推荐" },
  { title: "政策解读", desc: "考研政策变化与注意事项" },
  { title: "学专对比", desc: "学硕与专硕的区别与选择建议" }
];

features.forEach((feat, i) => {
  const x = 0.5 + (i % 3) * 3.1;
  const y = 1.15 + Math.floor(i / 3) * 2.2;
  
  // Card
  slide4.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 2.9, h: 2.0,
    fill: { color: COLORS.white },
    shadow: makeShadow()
  });
  
  // Icon circle
  slide4.addShape(pres.shapes.OVAL, {
    x: x + 1.05, y: y + 0.2, w: 0.8, h: 0.8,
    fill: { color: COLORS.accent }
  });
  
  // Number
  slide4.addText(String(i + 1), {
    x: x + 1.05, y: y + 0.3, w: 0.8, h: 0.6,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: COLORS.white, align: "center", valign: "middle", margin: 0
  });
  
  // Title
  slide4.addText(feat.title, {
    x: x + 0.15, y: y + 1.1, w: 2.6, h: 0.4,
    fontSize: 16, fontFace: "Microsoft YaHei", bold: true,
    color: COLORS.darkText, align: "center", margin: 0
  });
  
  // Description
  slide4.addText(feat.desc, {
    x: x + 0.15, y: y + 1.5, w: 2.6, h: 0.4,
    fontSize: 12, fontFace: "Microsoft YaHei",
    color: COLORS.mutedText, align: "center", margin: 0
  });
});

// ==================== SLIDE 5: Data Overview ====================
let slide5 = pres.addSlide();
slide5.background = { color: COLORS.lightGray };

// Header
slide5.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.darkBg }
});
slide5.addText("数据概览", {
  x: 0.5, y: 0.2, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei", bold: true,
  color: COLORS.white, margin: 0
});

// Big stats
const stats = [
  { num: "102", label: "收录院校", unit: "所" },
  { num: "1216", label: "问答知识", unit: "条" },
  { num: "26", label: "学科评估", unit: "个" },
  { num: "34", label: "自划线院校", unit: "所" }
];

stats.forEach((stat, i) => {
  const x = 0.5 + i * 2.4;
  
  // Stat card
  slide5.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.2, w: 2.2, h: 2.0,
    fill: { color: COLORS.white },
    shadow: makeShadow()
  });
  
  // Top accent
  slide5.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.2, w: 2.2, h: 0.08,
    fill: { color: COLORS.accent }
  });
  
  // Number
  slide5.addText(stat.num, {
    x: x, y: 1.4, w: 2.2, h: 0.9,
    fontSize: 48, fontFace: "Arial", bold: true,
    color: COLORS.darkBg, align: "center", margin: 0
  });
  
  // Unit
  slide5.addText(stat.unit, {
    x: x, y: 2.2, w: 2.2, h: 0.4,
    fontSize: 16, fontFace: "Microsoft YaHei",
    color: COLORS.mutedText, align: "center", margin: 0
  });
  
  // Label
  slide5.addText(stat.label, {
    x: x, y: 2.7, w: 2.2, h: 0.4,
    fontSize: 14, fontFace: "Microsoft YaHei", bold: true,
    color: COLORS.darkText, align: "center", margin: 0
  });
});

// Data sources section
slide5.addText("数据来源", {
  x: 0.5, y: 3.5, w: 9, h: 0.4,
  fontSize: 18, fontFace: "Microsoft YaHei", bold: true,
  color: COLORS.darkText, margin: 0
});

const sources = [
  "985/211高校数据 | 教育部学科评估 | 历年分数线 | 招生简章",
  "初试科目大纲 | 考研政策文件 | 学长学姐经验 | 就业数据"
];
sources.forEach((src, i) => {
  slide5.addText(src, {
    x: 0.5, y: 4.0 + i * 0.5, w: 9, h: 0.4,
    fontSize: 13, fontFace: "Microsoft YaHei",
    color: COLORS.mutedText, margin: 0
  });
});

// ==================== SLIDE 6: Smart Recommendations ====================
let slide6 = pres.addSlide();
slide6.background = { color: COLORS.lightGray };

// Header
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.darkBg }
});
slide6.addText("智能推荐算法", {
  x: 0.5, y: 0.2, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei", bold: true,
  color: COLORS.white, margin: 0
});

// Flow diagram
const flowSteps = [
  { text: "用户输入", desc: "分数+背景" },
  { text: "智能分析", desc: "提取关键信息" },
  { text: "院校匹配", desc: "按层次筛选" },
  { text: "性价比排序", desc: "评估+分数线" },
  { text: "推荐结果", desc: "Top6院校" }
];

flowSteps.forEach((step, i) => {
  const x = 0.4 + i * 1.9;
  
  // Circle
  slide6.addShape(pres.shapes.OVAL, {
    x: x, y: 1.3, w: 1.4, h: 1.4,
    fill: { color: i === flowSteps.length - 1 ? COLORS.accent : COLORS.mediumBg }
  });
  
  // Step number
  slide6.addText(String(i + 1), {
    x: x, y: 1.5, w: 1.4, h: 0.6,
    fontSize: 24, fontFace: "Arial", bold: true,
    color: COLORS.white, align: "center", margin: 0
  });
  
  // Step text
  slide6.addText(step.text, {
    x: x, y: 2.15, w: 1.4, h: 0.4,
    fontSize: 12, fontFace: "Microsoft YaHei", bold: true,
    color: COLORS.darkText, align: "center", margin: 0
  });
  
  // Arrow
  if (i < flowSteps.length - 1) {
    slide6.addText("→", {
      x: x + 1.4, y: 1.75, w: 0.5, h: 0.5,
      fontSize: 24, color: COLORS.mutedText, align: "center", margin: 0
    });
  }
});

// Algorithm details
slide6.addText("推荐逻辑", {
  x: 0.5, y: 3.0, w: 9, h: 0.4,
  fontSize: 18, fontFace: "Microsoft YaHei", bold: true,
  color: COLORS.darkText, margin: 0
});

const algoDetails = [
  { score: "≥ 340分", level: "985顶尖院校", example: "浙大、哈工大、电子科大" },
  { score: "280-339分", level: "211/普通王牌", example: "南邮、杭电、浙工大" },
  { score: "< 280分", level: "普通院校优先", example: "重邮、深大、广大" }
];

algoDetails.forEach((detail, i) => {
  const y = 3.5 + i * 0.65;
  
  // Score badge
  slide6.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: y, w: 1.8, h: 0.55,
    fill: { color: COLORS.accent }
  });
  slide6.addText(detail.score, {
    x: 0.5, y: y, w: 1.8, h: 0.55,
    fontSize: 13, fontFace: "Microsoft YaHei", bold: true,
    color: COLORS.white, align: "center", valign: "middle", margin: 0
  });
  
  // Level
  slide6.addText(detail.level, {
    x: 2.5, y: y, w: 2.5, h: 0.55,
    fontSize: 14, fontFace: "Microsoft YaHei", bold: true,
    color: COLORS.darkText, valign: "middle", margin: 0
  });
  
  // Example
  slide6.addText(detail.example, {
    x: 5.2, y: y, w: 4.3, h: 0.55,
    fontSize: 13, fontFace: "Microsoft YaHei",
    color: COLORS.mutedText, valign: "middle", margin: 0
  });
});

// ==================== SLIDE 7: Technical Highlights ====================
let slide7 = pres.addSlide();
slide7.background = { color: COLORS.lightGray };

// Header
slide7.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: COLORS.darkBg }
});
slide7.addText("技术亮点", {
  x: 0.5, y: 0.2, w: 9, h: 0.5,
  fontSize: 28, fontFace: "Microsoft YaHei", bold: true,
  color: COLORS.white, margin: 0
});

// Tech highlights - left column
const techLeft = [
  { title: "离线运行", desc: "无需网络连接，数据全部本地存储" },
  { title: "快速响应", desc: "基于规则的匹配，毫秒级返回答案" },
  { title: "灵活扩展", desc: "支持添加新的问答数据和院校信息" }
];

techLeft.forEach((tech, i) => {
  const y = 1.15 + i * 1.4;
  
  // Card
  slide7.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: y, w: 4.3, h: 1.25,
    fill: { color: COLORS.white },
    shadow: makeShadow()
  });
  
  // Left accent
  slide7.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: y, w: 0.08, h: 1.25,
    fill: { color: COLORS.accent }
  });
  
  slide7.addText(tech.title, {
    x: 0.75, y: y + 0.15, w: 3.9, h: 0.4,
    fontSize: 16, fontFace: "Microsoft YaHei", bold: true,
    color: COLORS.darkText, margin: 0
  });
  
  slide7.addText(tech.desc, {
    x: 0.75, y: y + 0.6, w: 3.9, h: 0.5,
    fontSize: 13, fontFace: "Microsoft YaHei",
    color: COLORS.mutedText, margin: 0
  });
});

// Right column
const techRight = [
  { title: "多模式支持", desc: "Web界面、命令行、API多种使用方式" },
  { title: "智能理解", desc: "自动提取用户分数和背景信息" },
  { title: "性价比分析", desc: "综合评估等级与分数线进行排序" }
];

techRight.forEach((tech, i) => {
  const y = 1.15 + i * 1.4;
  
  // Card
  slide7.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: y, w: 4.3, h: 1.25,
    fill: { color: COLORS.white },
    shadow: makeShadow()
  });
  
  // Left accent
  slide7.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: y, w: 0.08, h: 1.25,
    fill: { color: COLORS.mediumBg }
  });
  
  slide7.addText(tech.title, {
    x: 5.45, y: y + 0.15, w: 3.9, h: 0.4,
    fontSize: 16, fontFace: "Microsoft YaHei", bold: true,
    color: COLORS.darkText, margin: 0
  });
  
  slide7.addText(tech.desc, {
    x: 5.45, y: y + 0.6, w: 3.9, h: 0.5,
    fontSize: 13, fontFace: "Microsoft YaHei",
    color: COLORS.mutedText, margin: 0
  });
});

// ==================== SLIDE 8: Summary ====================
let slide8 = pres.addSlide();
slide8.background = { color: COLORS.darkBg };

// Decorative elements
slide8.addShape(pres.shapes.OVAL, {
  x: -1.5, y: 3.5, w: 4, h: 4,
  fill: { color: COLORS.mediumBg, transparency: 50 }
});
slide8.addShape(pres.shapes.OVAL, {
  x: 8, y: -0.5, w: 3, h: 3,
  fill: { color: COLORS.accent, transparency: 60 }
});

// Title
slide8.addText("总结", {
  x: 0.5, y: 0.8, w: 9, h: 0.7,
  fontSize: 36, fontFace: "Microsoft YaHei", bold: true,
  color: COLORS.white, align: "center"
});

// Summary points
const summaryPoints = [
  "专注考研择校场景的垂直领域问答系统",
  "本地运行，保护隐私，无需联网",
  "智能推荐算法，基于用户分数提供个性化建议",
  "数据持续更新，覆盖全面",
  "多端适配：Web界面 / 命令行 / API"
];

summaryPoints.forEach((point, i) => {
  // Checkmark circle
  slide8.addShape(pres.shapes.OVAL, {
    x: 1.5, y: 1.8 + i * 0.65, w: 0.35, h: 0.35,
    fill: { color: COLORS.accent }
  });
  slide8.addText("✓", {
    x: 1.5, y: 1.82 + i * 0.65, w: 0.35, h: 0.3,
    fontSize: 14, fontFace: "Arial", bold: true,
    color: COLORS.white, align: "center", margin: 0
  });
  
  // Point text
  slide8.addText(point, {
    x: 2.0, y: 1.8 + i * 0.65, w: 6.5, h: 0.35,
    fontSize: 16, fontFace: "Microsoft YaHei",
    color: COLORS.white, valign: "middle", margin: 0
  });
});

// Call to action
slide8.addShape(pres.shapes.RECTANGLE, {
  x: 2.5, y: 5.0, w: 5, h: 0.45,
  fill: { color: COLORS.accent }
});
slide8.addText("运行命令: python main.py", {
  x: 2.5, y: 5.0, w: 5, h: 0.45,
  fontSize: 14, fontFace: "Consolas",
  color: COLORS.white, align: "center", valign: "middle", margin: 0
});

// Save
pres.writeFile({ fileName: "考研择校问答系统_项目介绍.pptx" })
  .then(() => console.log("PPT created successfully!"))
  .catch(err => console.error(err));