# RetroNest Updates

Public files the RetroNest app reads over GitHub Pages. No app code lives here.

| File | Used for |
|---|---|
| `config.json` | Announcements and community links shown on the app's News & Support page |
| `privacy.html` | Privacy policy linked from the app and from the store listing |
| `privacy-tr.html` | The same policy in Turkish |
| `data/nointro/` | Game name tables bundled with the app (CC BY-SA 4.0, see `data/README.md`) |

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

