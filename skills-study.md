# Skills 使用指南

## 安装 Skills

### 从 GitHub 仓库安装
```bash
npx skills add https://github.com/anthropics/skills --skill frontend-design
```

### 安装过程说明
- 安装时会列出支持的 54 种 AI 编程助手（Amp、Cline、Cursor、Qwen Code 等）
- 安装 scope 为全局（Global）
- 安装完成后会进行安全风险评估（Gen、Socket、Snyk）

## 查看已安装的 Skills

```bash
npx skills list
```

或直接查看安装目录：
```bash
ls -la ~/.agents/skills/
```

## 卸载 Skills

### 方法一：使用命令卸载（推荐）
```bash
npx skills remove <skill-name>
```

示例：
```bash
npx skills remove frontend-design
```

### 方法二：手动删除目录
```bash
rm -rf ~/.agents/skills/<skill-name>
```

示例：
```bash
rm -rf ~/.agents/skills/frontend-design
rm -rf ~/.agents/skills/find-skills
```

> **建议**：优先使用 `npx skills remove` 命令，因为它会正确清理所有相关配置和引用。

## 使用 Skills

### 在 Qwen Code 中
重启 Qwen Code 后，通过以下命令调用：
```
/skill frontend-design
```

### 自动发现
系统会自动发现 `~/.agents/skills/` 目录下的 Skills，在使用 `/agent` 时可用。

## 安装目录

**全局安装位置：**
```
~/.agents/skills/
```

每个 Skill 会被复制到此目录下，以 Skill 名称命名的子目录中。
