# Rethlas Claude Code Plugin

[`frenzymath/Rethlas`](https://github.com/frenzymath/Rethlas) 的 Claude Code 打包层。所有 credit 归 frenzymath 与上游贡献者。

## 安装

```bash
claude plugin marketplace add pikel72/Rethlas-Claude
claude plugin install rethlas@rethlas-claude
```

MCP 服务器需要 Python 包。先用 `claude plugin details rethlas` 拿到插件安装路径,然后:

```bash
pip install -r <plugin-path>/solver/mcp/requirements.txt \
            -r <plugin-path>/verifier/mcp/requirements.txt
```

## 许可证

[Apache License 2.0](LICENSE),沿用上游。