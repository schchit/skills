# Book Selection Logic

## Weekday-Based Categories

| Weekday | Category |
|---------|----------|
| Monday | Business Strategy |
| Tuesday | Psychology |
| Wednesday | Technology |
| Thursday | Economics |
| Friday | Innovation |
| Saturday | Philosophy |
| Sunday | Biography |

## Selection Algorithm

1. **Determine category** based on current weekday
2. **Filter books** where `used == false` in that category
3. **Check used_models** to avoid repeating models
4. **If category exhausted**, pick from other categories
5. **Mark as used** after selection

## JSON Structure

```json
{
  "books": [
    {
      "title": "Book Title",
      "author": "Author Name",
      "category": "Business Strategy",
      "used": false,
      "used_models": []
    }
  ]
}
```

## Adding New Books

When adding books to reading-history.json:
- Set `used: false`
- Initialize `used_models: []`
- Choose appropriate category
- Ensure title and author are accurate
