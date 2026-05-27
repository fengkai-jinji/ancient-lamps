# Git Push Script
# 刷新环境变量
$env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH", "User")

# 配置代理（如果需要）
git config --global http.proxy http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897

# 配置远程仓库
git remote set-url origin https://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@github.com/fengkai-jinji/ancient-lamps.git

# 检查状态
Write-Host "检查 Git 状态..."
git status

# 查看提交历史
Write-Host "`n最近的提交记录："
git log --oneline -5

# 推送到 GitHub
Write-Host "`n正在推送到 GitHub..."
git push -u origin main

Write-Host "`n推送完成！"
