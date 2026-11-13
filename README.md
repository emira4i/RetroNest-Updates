# RetroNest Updates

Public files the RetroNest app reads over GitHub Pages. No app code lives here.

| File | Used for |
|---|---|
| `config.json` | Announcements and community links shown on the app's News & Support page |
| `privacy.html` | Privacy policy linked from the app and from the store listing |

Served from `https://emira4i.github.io/RetroNest-Updates/`.

## config.json

```json
{
  "version": 1,
  "announcements": [
    {
      "id": "unique-id",
      "title": {"en": "Title", "tr": "Başlık"},
      "body": {"en": "Text", "tr": "Metin"},
      "url": "https://t.me/retronestapp",
      "start": "2026-12-01T00:00:00Z",
      "end": "2026-12-31T00:00:00Z",
      "audience": "all",
      "minVersionCode": 1,
      "maxVersionCode": 99
    }
  ],
  "links": [
    {"id": "telegram", "kind": "telegram", "url": "https://t.me/retronestapp", "label": {"en": "Telegram channel"}}
  ]
}
```

- `version` must stay `1`; the app ignores a file with another version.
- Only `id`, `title` and `body` are required for an announcement. `audience` is `all`, `free` or `premium`.
- An announcement the user dismissed stays dismissed; use a new `id` to show a new one.
- Links must be `https` and point to a host the app allows: this site, github.com, t.me, telegram.me, discord.gg, discord.com, instagram.com, tiktok.com, youtube.com, youtu.be, play.google.com.
- The file must stay valid JSON: a broken file is ignored and the app keeps its last good copy.
