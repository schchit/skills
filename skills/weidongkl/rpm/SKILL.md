# RPM Skill - RPM 包管理

## 技能描述 | Skill Description

**名称 | Name:** rpm  
**版本 | Version:** 1.0.0  
**作者 | Author:** OS Build Agent  
**领域 | Domain:** RPM Package Management  

全面的 RPM 包管理技能，支持 RPM 包创建、查询、验证、签名、依赖分析等所有核心功能。

Comprehensive RPM Package Management skill with package creation, query, verification, signing, dependency analysis, and all core functionalities.

---

## 功能列表 | Features

### 1. RPM 查询 | RPM Query
- 查询已安装包 | Query installed packages
- 查询 RPM 文件 | Query RPM files
- 查询包信息/文件/依赖 | Query info/files/dependencies
- 查询 changelog/脚本 | Query changelog/scripts

### 2. RPM 创建 | RPM Creation
- 创建 spec 文件 | Create spec files
- 构建 SRPM/RPM | Build SRPM/RPM
- 本地构建 (mock) | Local build (mock)

### 3. RPM 验证 | RPM Verification
- 验证安装包 | Verify installed packages
- 校验和检查 | Checksum verification
- 签名验证 | Signature verification

### 4. RPM 签名 | RPM Signing
- GPG 签名 | GPG signing
- 签名验证 | Signature verification
- 密钥管理 | Key management

### 5. 依赖分析 | Dependency Analysis
- 列出依赖/反向依赖 | List dependencies/reverse deps
- 依赖解析 | Dependency resolution
- 冲突检测 | Conflict detection

### 6. 宏管理 | Macro Management
- 列出/定义宏 | List/define macros
- 宏展开/调试 | Macro expansion/debugging

### 7. 数据库管理 | Database Management
- 重建/清理数据库 | Rebuild/clean database
- 导入/导出 | Import/export

---

## 配置 | Configuration

### RPM 配置文件 | RPM Config Files

```bash
# 主配置 | Main config
/etc/rpmrc
/etc/rpm/macros

# 用户配置 | User config
~/.rpmmacros
~/.rpmrc
```

### 常用宏定义 | Common Macros

```bash
# ~/.rpmmacros
%packager Your Name
%_topdir %(echo $HOME)/rpmbuild
%_gpg_name your-gpg-key-id
```

---

## 使用示例 | Usage Examples

### RPM 查询 | RPM Query

```bash
# 查询已安装包
# Query installed package
rpm -qa | grep httpd
rpm -qi httpd

# 查询包文件列表
# Query package files
rpm -ql httpd

# 查询包依赖
# Query package dependencies
rpm -qR httpd

# 查询包提供
# Query package provides
rpm -q --provides httpd

# 查询 changelog
# Query changelog
rpm -q --changelog httpd

# 查询包脚本
# Query package scripts
rpm -q --scripts httpd

# 查询文件归属
# Query file ownership
rpm -qf /etc/httpd/conf/httpd.conf

# 查询配置文件
# Query config files
rpm -qc httpd

# 查询文档文件
# Query documentation files
rpm -qd httpd
```

### RPM 创建 | RPM Creation

```bash
# 创建目录结构
# Create directory structure
rpmdev-setuptree

# 创建 spec 文件
# Create spec file
rpmdev-newspec -o mypackage.spec mypackage

# 下载源码
# Download sources
spectool -g -R mypackage.spec

# 构建 SRPM
# Build SRPM
rpmbuild -bs mypackage.spec

# 构建 RPM
# Build RPM
rpmbuild -ba mypackage.spec

# 构建二进制包
# Build binary packages only
rpmbuild -bb mypackage.spec

# 构建源码包
# Build source package only
rpmbuild -bs mypackage.spec

# 使用 mock 构建
# Build with mock
mock -r fedora-39-x86_64 mypackage.spec
```

### Spec 文件模板 | Spec File Template

```spec
Name:           mypackage
Version:        1.0.0
Release:        1%{?dist}
Summary:        Package summary

License:        MIT
URL:            https://example.com
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  gcc, make
Requires:       glibc >= 2.17

%description
Detailed package description.

%prep
%setup -q

%build
%configure
%make_build

%install
%make_install

%files
%doc README.md LICENSE
%{_bindir}/myapp

%changelog
* Mon Mar 23 2026 Your Name <your@email.com> - 1.0.0-1
- Initial package
```

### RPM 验证 | RPM Verification

```bash
# 验证所有包
# Verify all packages
rpm -Va

# 验证特定包
# Verify specific package
rpm -V httpd

# 验证配置文件
# Verify config files
rpm -Vf /etc/httpd/conf/httpd.conf
```

### RPM 签名 | RPM Signing

```bash
# 签名 RPM 包
# Sign RPM package
rpm --addsign ./mypackage-1.0-1.x86_64.rpm

# 重新签名
# Resign
rpm --resign ./mypackage-1.0-1.x86_64.rpm

# 删除签名
# Delete signature
rpm --delsign ./mypackage-1.0-1.x86_64.rpm

# 检查签名
# Check signature
rpm -K ./mypackage-1.0-1.x86_64.rpm

# 导入 GPG 密钥
# Import GPG key
rpm --import RPM-GPG-KEY-example

# 列出 GPG 密钥
# List GPG keys
rpm -qa gpg-pubkey*
```

### 依赖分析 | Dependency Analysis

```bash
# 查找提供命令的包
# Find package providing command
rpm -qf $(which command)

# 查找提供文件的包
# Find package providing file
rpm -qf /path/to/file

# 查找提供依赖的包
# Find package providing dependency
rpm -q --whatprovides libexample.so

# 查找依赖某包的包
# Find packages requiring this package
rpm -q --whatrequires httpd

# 检查未满足依赖
# Check unsatisfied dependencies
rpm -qp --requires ./package.rpm
```

### 宏管理 | Macro Management

```bash
# 列出所有宏
# List all macros
rpm --showrc

# 列出特定宏
# List specific macro
rpm --eval '%{_topdir}'

# 展开宏
# Expand macro
rpm --eval '%{name}'

# 定义宏
# Define macro
echo '%_my_macro value' >> ~/.rpmmacros
```

### 数据库管理 | Database Management

```bash
# 重建 RPM 数据库
# Rebuild RPM database
rpm --rebuilddb

# 验证数据库
# Verify database
rpm --verifydb

# 清理数据库
# Clean database
rpm --clean
```

---

## 命令参考 | Command Reference

| 命令 | 描述 | Description |
|------|------|-------------|
| `rpm -qa` | 查询所有已安装包 | Query all installed |
| `rpm -qi` | 包信息 | Package info |
| `rpm -ql` | 包文件列表 | Package files |
| `rpm -qR` | 包依赖 | Package requires |
| `rpm -qc` | 配置文件 | Config files |
| `rpm -qd` | 文档文件 | Documentation files |
| `rpm -qf` | 文件归属 | File ownership |
| `rpm -V` | 验证包 | Verify package |
| `rpm -Va` | 验证所有包 | Verify all |
| `rpm -K` | 检查签名 | Check signature |
| `rpm --addsign` | 签名包 | Sign package |
| `rpm --import` | 导入密钥 | Import key |
| `rpm --rebuilddb` | 重建数据库 | Rebuild database |
| `rpmbuild -ba` | 构建 SRPM+RPM | Build SRPM+RPM |
| `rpmbuild -bs` | 构建 SRPM | Build SRPM |
| `rpmbuild -bb` | 构建 RPM | Build RPM |

---

## 最佳实践 | Best Practices

### 1. Spec 文件编写 | Spec File Writing
- 遵循打包指南 | Follow packaging guidelines
- 明确声明依赖 | Declare dependencies explicitly
- 使用正确的宏 | Use correct macros

### 2. 质量控制 | Quality Control
- 运行 rpmlint | Run rpmlint
- 验证签名 | Verify signatures
- 测试安装 | Test installation

### 3. 版本管理 | Version Management
- 遵循语义化版本 | Follow semantic versioning
- 维护 changelog | Maintain changelog

---

## 故障排除 | Troubleshooting

### 构建失败 | Build Failed
```bash
# 详细构建日志
# Verbose build log
rpmbuild -vv -ba mypackage.spec

# 检查依赖
# Check dependencies
rpmlint mypackage.spec
```

### 签名失败 | Sign Failed
```bash
# 检查 GPG 密钥
# Check GPG key
gpg --list-keys

# 检查密钥权限
# Check key permissions
ls -la ~/.gnupg/
```

### 依赖问题 | Dependency Issues
```bash
# 查找提供者
# Find provider
dnf provides libexample.so
# 或 | or
yum provides libexample.so
```

---

## 参考资料 | References

- [RPM 官方文档 | RPM Official Docs](https://rpm.org/documentation.html)
- [Fedora 打包指南 | Fedora Packaging Guide](https://docs.fedoraproject.org/en-US/packaging-guidelines/)
- [openSUSE 打包指南 | openSUSE Packaging Guide](https://en.opensuse.org/openSUSE:Packaging_guidelines)

---

## 许可证 | License

MIT License

---

## 更新日志 | Changelog

### v1.0.0 (2026-03-23)
- 初始版本，完整的 RPM 管理支持
- Initial release with full RPM management coverage
- 中英文双语文档
- Bilingual documentation (Chinese/English)
