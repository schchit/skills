# Community Connector

A skill that helps users find and connect with local community resources, events, and support groups based on their interests and needs.

## Description

Community Connector helps users discover local community resources, events, volunteer opportunities, and support groups. It provides personalized recommendations based on user interests, location, and availability.

## Usage

```bash
# Basic usage
community-connector find --interest "gardening" --location "Beijing"

# Find events
community-connector events --date "2026-04-10"

# Get recommendations
community-connector recommend --profile "new_parent"
```

## Input/Output

**Input**: User interests, location, availability, specific needs
**Output**: Curated list of community resources with contact info, event details, and connection guidance

## Examples

```bash
$ community-connector find --interest "yoga" --location "Haidian"
Found 3 community resources:
1. Haidian Community Yoga Group (meets weekly)
2. Beijing Yoga Enthusiasts (online community)
3. Local Wellness Center (free trial classes)
```

## Development

See design document: `/Users/jianghaidong/.openclaw/workspace/shared/projects/community-connector-design.md`
