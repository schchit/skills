# GitHub Announcement

I upgraded `one-person-company-os` to `v0.6.7`.

The previous release fixed marketplace trust and safety boundaries.
This release fixes the next usability gap: a downloaded workspace still looked too much like a pile of markdown source files.

What changed:

- every generated workspace now includes a localized HTML reading layer
- Chinese founders now get `阅读版/00-先看这里.html`
- English founders now get `reading/00-start-here.html`
- the core dashboard, offer, pipeline, product, delivery, cash, asset, and deliverable-overview pages now export as reading-friendly HTML files
- markdown remains the editable working source, while numbered DOCX files still carry the formal deliverables

This matters because a one-person-company operating system should not only be runnable.
It should also be easy to download, open, and understand immediately.
