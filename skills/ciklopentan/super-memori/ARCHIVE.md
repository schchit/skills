# Super Memory Skill (legacy archive note)

Этот файл теперь относится к legacy/v2-этапу навыка. Актуальный v3-проектный контракт см. в `SKILL.md` и `references/`.

Навык семантического поиска по памяти. Пройден 3 раунда Dual Thinking с DeepSeek.

**Дата создания:** 2026-04-05  
**Статус:** Архив — не установлен как активный навык  
**Причина:** Отложен пока память не вырастет  

## Для активации:
1. `pip install sentence-transformers`
2. Переместить в skills/ и добавить в AGENTS.md
3. Первый запуск: `bash index-daily.sh`
4. Cron: `0 2 * * * ~/.openclaw/skills/super_memori/index-daily.sh`

## Dual Thinking итог:
- Round 1: 5 слепых пятен найдено, overengineering остановлен
- Round 2: Архитектура подтверждена, Qdrant выбран
- Round 3: "Ready to ship after 2 fixes" — оба внесены
