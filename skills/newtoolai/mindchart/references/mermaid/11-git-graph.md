# Git Graph

## Diagram Description
A Git graph visually displays the commit history, branches, and merge situations of a Git repository. It helps understand project version evolution and branch strategies.

## Applicable Scenarios
- Git repository history display
- Branch strategy documentation
- Pull Request flow explanation
- Merge conflict analysis
- Release version tracking

## Syntax Examples

```mermaid
gitGraph
    commit id: "Initial commit"
    commit id: "Add basic functionality"
    branch feature
    checkout feature
    commit id: "Develop new feature - 1"
    commit id: "Develop new feature - 2"
    checkout main
    commit id: "Fix bug"
    merge feature id: "Merge feature branch"
    commit id: "Release v1.0"
```

```mermaid
gitGraph
    commit id: "Initialize project"
    commit id: "Add README"
    branch develop
    checkout develop
    commit id: "Feature development - 1"
    commit id: "Feature development - 2"
    branch feature-xyz
    checkout feature-xyz
    commit id: "XYZ feature development"
    checkout develop
    merge feature-xyz id: "Merge XYZ"
    checkout main
    merge develop id: "Release version"
    commit id: "Hotfix fix"
    merge main id: "Merge fix"
```

## Syntax Reference

### Basic Syntax
```mermaid
gitGraph
    commit id: "Commit message"
    commit
    branch BranchName
    checkout BranchName
    commit id: "Commit message"
```

### Commits
- `commit`: Create commit (with auto ID)
- `commit id: "message"`: Create commit with ID and message

### Branch Operations
- `branch Name`: Create new branch
- `checkout Name`: Switch to specified branch
- `cherry-pick CommitID`: Cherry-pick specific commit

### Merge Operations
- `merge Name`: Merge branch into current branch
- `merge Name id: "merge message"`: Merge with message

### Tags
```mermaid
gitGraph
    commit id: "v1.0.0"
    commit id: "v1.0.1" tag: "v1.0.1"
    commit id: "v2.0.0" tag: "v2.0.0"
```

### Rebase
```mermaid
gitGraph
    commit
    branch feature
    checkout feature
    commit
    checkout main
    rebase feature
```

## Configuration Reference

| Option | Description |
|--------|-------------|
| showCommitLabel | Show commit labels |
| mainBranchName | Main branch name |
| mainBranchOrder | Main branch order |
| showBranches | Show branches |
| mode | Graphics mode |

### Theme Configuration
```mermaid
gitGraph
    config
        commitSpacing 30
        nodeSpacing 50
```
