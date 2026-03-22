# ============ 安全检测规则配置 ============
# 可独立维护的检测规则模块
# 格式: { '语言': [正则表达式列表] }
# 语言标识: py, sh, js, ts, all(所有语言)

# Check 1: 凭证关键词
CRED_PATTERNS = {
    'py': [r'os\.environ|getenv', r'api[_-]?key|secret[_-]?key|password|credential', r'private[_-]?key|mnemonic|seed[_-]?phrase'],
    'sh': [r'\$API_KEY|\$SECRET|\$TOKEN|\$PASSWORD', r'\${[A-Z_]+}', r'\.env|\.aws|\.ssh'],
    'js': [r'process\.env', r'apiKey|api_key|secretKey', r'\.env'],
}

# Check 2: 代码执行
EXEC_PATTERNS = {
    'py': [r'eval\s*\(|exec\s*\(', r'subprocess\.call.*shell\s*=\s*True', r'os\.system|os\.popen', r'__import__\s*\('],
    'sh': [r'eval\s+', r'exec\s+', r'`[^`]+`', r'\$\([^)]+\)', r'bash\s+-c'],
    'js': [r'eval\s*\(', r'child_process|spawn\(|execSync', r'Function\s*\(', r'require\s*\(\s*[\'"]child_process'],
}

# Check 3: 数据外泄 URL
EXFIL_PATTERNS = {
    'all': [r'webhook\.site|requestbin|ngrok\.io', r'pipedream\.net|hookbin|beeceptor', r'requestcatcher|postb\.in|httpbin\.org', r'myjson\.com|jsonblob\.io'],
}

# Check 4: Base64 混淆
B64_PATTERNS = {
    'py': [r'atob\(|btoa\(|base64\.decode'],
    'sh': [r'base64\s+-d|base64\s+--decode'],
    'js': [r'atob\(|btoa\(|Buffer\.from.*base64'],
}

# Check 5: 敏感文件系统
FS_PATTERNS = {
    'py': [r'/etc/passwd|/etc/shadow', r'~/.ssh|~/.gnupg|~/.aws'],
    'sh': [r'/etc/passwd|/etc/shadow', r'~\/\.ssh|~\/\.gnupg'],
    'js': [r'\/etc\/passwd', r'\.ssh\/|\.gnupg\/'],
}

# Check 6: 加密钱包地址
CRYPTO_PATTERNS = {
    'all': [r'0x[a-fA-F0-9]{40}', r'bc1[a-zA-HJ-NP-Z0-9]{39,59}', r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}'],
}

# Check 7: 依赖混淆/拼写抢注
PKG_PATTERNS = {
    'all': [r'@internal|@private|@corp|@company', r'-internal-|-private-', r'requets|reqeusts|lodasg|loadsh|colosr|axois'],
}

# Check 8: 安装钩子
HOOK_PATTERNS = {
    'all': [r'postinstall|preinstall|post_install|pre_install', r'setup\.py.*install'],
}

# Check 9: Symlink 攻击
SYMLINK_PATTERNS = {
    'py': [r'os\.symlink|fs\.symlinkSync'],
    'sh': [r'ln\s+-s'],
    'js': [r'fs\.symlink|symlink\('],
}

# Check 10: 时间炸弹
TIMEBOMB_PATTERNS = {
    'py': [r'Date\.now|datetime\.now', r'setTimeout|setInterval'],
    'sh': [r'at\s+|crontab'],
    'js': [r'setTimeout|setInterval|Date\.now'],
}

# Check 11: 远程脚本执行
REMOTE_EXEC_PATTERNS = {
    'all': [r'curl\s+.*\|\s*bash|wget\s+.*\|\s*bash', r'curl\s+.*sh\b|wget\s+.*sh\b'],
}

# Check 12: 遥测/追踪
TELEMETRY_PATTERNS = {
    'all': [r'google-analytics|gtag|ga\(', r'segment\.|mixpanel|amplitude|hotjar'],
}

# Check 13: 不寻常端口
PORT_PATTERNS = {
    'all': [r':\d{4,5}[/"\']'],
}

# Check 14: 提示词注入
PROMPT_INJECTION = {
    'all': [r'ignore.*previous instructions', r'disregard.*previous|forget your rules', r'you are now |act as |pretend to be', r'override.*(safety|security|rules)'],
}

# Check 15: 隐蔽数据外发
STEALTH_EXFIL = {
    'all': [r'send.*(data|files?|secrets?|tokens?) to', r'POST.*(data|files?|secrets?)'],
}

# Check 16: C2 服务器
C2_PATTERNS = {
    'all': [r'91\.92\.242\.30'],
}

# Check 17: 容器逃逸
CONTAINER_ESCAPE = {
    'all': [r'docker.*socket|\.docker\.sock', r'cgroup\.escape|\.namespace'],
}

# Check 18: SSH 远程连接
SSH_PATTERNS = {
    'all': [r'ssh\s+-|scp\s+', r'paramiko|netmiko', r'fabric\.operations'],
}

# Check 19: 权限提升
PRIVILEGE_ESCALATION = {
    'all': [r'sudo\s+', r'chmod\s+777', r'setuid|setgid', r'chown\s+'],
}

# Check 20: 隐藏文件
HIDDEN_FILE = {
    'all': [r'\s\.\w+\s', r'open\s*\(\s*["\']\/\\.\w+'],
}

# Check 21: 非寻常端口
UNUSUAL_PORTS = {
    'all': [r':4444', r':5555', r':6666', r':7777', r':8888', r':9999', r':1337', r':31337', r':31338'],
}

# Check 22: 访问用户敏感文件 (借鉴自 skill-vetter RED FLAGS)
USER_SENSITIVE_FILES = {
    'all': [r'MEMORY\.md', r'USER\.md', r'SOUL\.md', r'IDENTITY\.md', r'\.claw.*config'],
}

# Check 23: 代码混淆 (借鉴自 skill-vetter)
OBFUSCATED_CODE = {
    'all': [r'eval\s*\(.*base64', r'decode\s*\(.*atob', r'Function\s*\(\s*["\'].*\\x'],
}

# Check 24: 浏览器敏感数据 (借鉴自 skill-vetter)
BROWSER_SENSITIVE = {
    'all': [r'cookie|session', r'localStorage', r'sessionStorage', r'\.cookie'],
}

# 网络模式 (用于组合检测)
NET_PATTERNS = {
    'py': [r'urllib|requests\.|http\.|https\.', r'os\.system.*curl|wget'],
    'sh': [r'curl |wget |fetch ', r'http|https'],
    'js': [r'axios|fetch|request|got\('],
}

# 检测项清单
SECURITY_CHECKS = [
    ("credential-harvest", "凭证收集", CRED_PATTERNS, "critical"),
    ("code-execution", "代码执行", EXEC_PATTERNS, "critical"),
    ("exfiltration-url", "数据外泄URL", EXFIL_PATTERNS, "critical"),
    ("base64-obfuscation", "Base64混淆", B64_PATTERNS, "medium"),
    ("sensitive-fs", "敏感文件系统", FS_PATTERNS, "critical"),
    ("crypto-wallet", "加密钱包地址", CRYPTO_PATTERNS, "critical"),
    ("dependency-confusion", "依赖混淆", PKG_PATTERNS, "high"),
    ("install-hook", "安装钩子", HOOK_PATTERNS, "medium"),
    ("symlink-attack", "Symlink攻击", SYMLINK_PATTERNS, "critical"),
    ("time-bomb", "时间炸弹", TIMEBOMB_PATTERNS, "medium"),
    ("remote-exec", "远程脚本执行", REMOTE_EXEC_PATTERNS, "critical"),
    ("telemetry", "遥测追踪", TELEMETRY_PATTERNS, "medium"),
    ("prompt-injection", "提示词注入", PROMPT_INJECTION, "critical"),
    ("stealth-exfil", "隐蔽数据外发", STEALTH_EXFIL, "critical"),
    ("c2-server", "C2服务器", C2_PATTERNS, "critical"),
    ("container-escape", "容器逃逸", CONTAINER_ESCAPE, "critical"),
    ("ssh-remote", "SSH远程连接", SSH_PATTERNS, "medium"),
    ("privilege-escalation", "权限提升", PRIVILEGE_ESCALATION, "critical"),
    ("hidden-file", "隐藏文件", HIDDEN_FILE, "warning"),
    ("unusual-ports", "非寻常端口", UNUSUAL_PORTS, "warning"),
    ("user-sensitive-files", "访问用户敏感文件", USER_SENSITIVE_FILES, "critical"),
    ("obfuscated-code", "代码混淆", OBFUSCATED_CODE, "critical"),
    ("browser-sensitive", "浏览器敏感数据", BROWSER_SENSITIVE, "critical"),
]

# 常见误报模式 (自动白名单)
FALSE_POSITIVE_PATTERNS = {
    r'API_KEY\s*=\s*["\']YOUR_',
    r'API_KEY\s*=\s*["\']xxx',
    r'https?://example\.com',
    r'https?://localhost',
    r'""".*api.*key.*"""',
    r"'''.*api.*key.*'''",
}

# 文档必要章节
REQUIRED_SKILL_SECTIONS = ['描述', '使用方法', '功能']

# 审计工具自身文件 (跳过检测)
AUDITOR_FILES = ['SKILL.md', 'skill_ict.py', 'skill_auditor.py', 'audit.sh', 'inspect.sh', 'trust_score.py', 'run_tests.py', 'rules.py']

# 支持的语言
SUPPORTED_LANGUAGES = {
    '.py': 'py',
    '.sh': 'sh',
    '.bash': 'sh',
    '.js': 'js',
    '.mjs': 'js',
    '.cjs': 'js',
    '.ts': 'ts',
    '.tsx': 'ts',
    '.jsx': 'ts',
}
