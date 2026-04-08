# Examples

## Publish now

User intent:

`Post this to Threads from main-brand right now`

Command:

```bash
threadsctl publish text --account main-brand --text "..." --confirmed
```

## Create a draft first

User intent:

`Prepare a Threads draft for review`

Command:

```bash
threadsctl draft create --account main-brand --type text --text "..." --created-by "OpenClaw"
```

## Publish an image

User intent:

`Post this image with a caption`

Command:

```bash
threadsctl publish image --account main-brand --media-url "https://example.com/image.jpg" --text "..." --alt-text "..." --confirmed
```

## Connect another Threads account

User intent:

`Connect a second Threads account called client-two`

Command:

```bash
threadsctl auth connect-url --label client-two
```

Then return the generated URL to the user and instruct them to complete OAuth in the browser.

## Inspect accounts

User intent:

`Show me connected Threads accounts`

Command:

```bash
threadsctl accounts list
```

## Inspect recent published posts

User intent:

`Show published posts for main-brand`

Command:

```bash
threadsctl published list --account main-brand
```
