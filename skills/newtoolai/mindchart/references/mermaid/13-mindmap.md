# Mind Map

## Diagram Description
A mind map is a diagram used for brainstorming, organizing thoughts, and visualizing relationships between concepts. It starts with a central idea and radiates outward with related topics.

## Applicable Scenarios
- Brainstorming and idea organization
- Knowledge structure visualization
- Study notes organization
- Project planning
- Decision making

## Syntax Examples

```mermaid
mindmap
    root((Mind Map))
        Primary Topic
            Secondary Topic A
                Tertiary Topic 1
                Tertiary Topic 2
            Secondary Topic B
                Tertiary Topic 3
        Another Primary
            Detail A
            Detail B
```

```mermaid
mindmap
    id1["中心主题"]
        id2["分支主题1"]
            id3["子主题1.1"]
            id4["子主题1.2"]
        id5["分支主题2"]
            id6["子主题2.1"]
            id7["子主题2.2"]
```

## Syntax Reference

### Basic Syntax
```mermaid
mindmap
    root((Central Idea))
        Topic 1
            Subtopic 1.1
            Subtopic 1.2
        Topic 2
            Subtopic 2.1
            Subtopic 2.2
```

### Node Shapes
- `((text))`: Central node (circle with double parentheses)
- `text`: Standard topic
- `["text"]`: Square bracket topic

### Hierarchy
- Root node: Central concept (only one)
- Level 2: Primary topics
- Level 3: Secondary topics
- Level 4: Tertiary topics (typically maximum depth)

### Multi-line Text
Use `<br>` for line breaks within nodes:
```mermaid
mindmap
    root((Multi-line<br>Node"))
        Topic ["Line 1<br>Line 2"]
```

## Configuration Reference

### Theme Customization
```mermaid
mindmap
    %%{init: {'theme': 'base'}}%%
    root((Theme Example))
        Topic
```

### Style Classes
```mermaid
mindmap
    root((Styled Mind Map))
        A["Customized"]
        B["Colored"]
        class A fill:#f9f,stroke:#333,color:red
        class B fill:#9f9,stroke:#333,color:green
```

### Notes
- Mind maps work best with a clear central concept
- Limit depth to 4-5 levels for readability
- Use concise labels for better visualization
- Consider using Chinese text directly (Mermaid supports Chinese)
