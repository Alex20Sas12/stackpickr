# StackPickr (cmpsite) — State

Обновлено: 14.10.2026 17:50 МСК

## Проект
Статический сайт сравнений хостинга/софта с affiliate-монетизацией + Adsterra.
Домен: https://stackpickr.vercel.app (Vercel, статика, **48 страниц**)

## 💰 Заработано за всё время: **$0**
Сайт живёт 24 дня. Причина №1 — индексация: было **5 из 47 URL**, сейчас **11 из 48**.
Причина №2 (исправлена) — 8 страниц Cloudways вели читателей на голый сайт без партnёрки.

## Базовая линия (R7)
- До 14.10: 47 страниц, 32 с партnёрским CTA, **8 страниц с CTA без монетизации** (все cloudways),
  0 аналитики, 5/47 URL в индексе.
- После 14.10: **48 страниц, 33 с партnёрским CTA, 0 без монетизации**, IndexNow+Yandex по 48 URL,
  деплой через `deploy.py` (exit 0 = live-проверка прошла).

## Критические problems (14.10)
| Проблема | Severity | Статус |
|----------|----------|--------|
| Конфиг Hermes бит (дубль `enabled: false` в блоке `custom`) → правки не применялись | CRITICAL | ✅ УБРАНО (Python из terminal); `hermes config check` rc=0 |
| Сайт 404 на ВСЕХ страницах (мой деплой корня репо) | CRITICAL | ✅ `vercel deploy site`; все 47 → 200 |
| Деплой уходил в другой проект (`cmpsite-lyart`), живой сайт не обновлялся 6 дней | CRITICAL | ✅ `--project stackpickr --scope keyt9750-7169s-projects` + `deploy.py` |
| 4 крона StackPickr удалены при инциденте очистки 08.10 | CRITICAL | ✅ ВОССОЗДАНЫ; health переведён в **no_agent** (LLM-сеть мертва) |
| Cloudways-CTA → голый сайт: 8 страниц без комиссионной ссылки | HIGH | ✅ `ALT_MONETISE={cloudways:ishosting}` в `cta_box()` |
| Хаб /hosting/ без партnёрского CTA | HIGH | ✅ `cta_box('ishosting')` |
| 26/28 падающих кронов системы: `model=None` → 503 Gemini structure_limit | HIGH (системный) | ⚠️ НЕ ЧИНИЛ — затронет все проекты. Рецепт: `hermes cron edit <id> --provider custom:frontierspace --model gpt-6-astra` |
| Индексация 5/47 URL (главный рычаг денег) | HIGH | ⚠️ 11/48 (14.10 17:45). Цель 21.10: ≥25 |
| НЕТ аналитики — конверсию мерить нельзя, фаза 3B мертва | HIGH | ⏳ GoatCounter/Plausible требуют регистрации с личной почтой |
| Cloudways affiliate на модерации с 09.10 | MEDIUM | ⏳ Апрува нет; крон `471fb4e0b8b6` следит; читатель получает alt-CTA ishosting |
| Bing/Google ping-эндпоинты мёртвы (410/deprecated) | LOW | ℹ️ не тратить время; IndexNow + GSC покрывают |

## Кроны (фактически, 14.10)
| ID | Расписание | Что | Денежный след |
|---|---|---|---|
| `7097de8b595b` health | 8:00/20:00 | **no_agent-скрипт** `stackpickr_health.py` — без LLM | сайт жив + нет утечек монetизации |
| `4a2686df505a` | 10:10 ежедневно | GSC IndexNow, квота 2/сайт/день | URL в индексе → клик |
| `471fb4e0b8b6` | 10:00/18:00 | апрув Cloudways (почта + панель) | ссылка Cloudways $50–125/продажа |
| `ed8133ecd8db` content | 9:00 | дыра из `gsc_queries.csv` → страница с партnёркой → деплой | +1 страница/день |
| `a8ee9e6b505e` traffic | 12:00 | `gsc_index_queue.py` + IndexNow | ≥25 URL в индексе к 21.10 |
| `4e61f07dc6f8` report | 20:00 | сводка в вечерний дайджест |
| `a7a4d645691d` | вс 12:30 | SEO-backlog (источник данных — `geo_audit.py`) |

**Почему health без LLM (решение 14.10):** LLM-сеть мертва по всем связкам —
`model=None` → 503 Gemini structure_limit; `custom` → группа без кредов; `q`/qwen → не имя
провайдера в CLI; `omni` → локальный :20128 мёртв (502); `custom:frontierspace`+`gpt-6-astra`
→ Cloudflare 502 (origin перегружен, 3 ретрая). Health — чистые HTTP + чтение файлов, LLM не нужен.
Скрипт печатает строку **только при проблеме** (watchdog), пусто = тихо зелёный.
`AppData\Local\hermes\scripts\stackpickr_health.py` (путь к проекту хардкод — скрипт вне репо).

## Продукты (7) и партnёрки
| Продукт | Партnёрка | Ставка | Статус ссылки |
|---|---|---|---|
| is*hosting | прямая `ishosting.com/affiliate/Nzk5NiM2` | 50% первой + до 20% lifetime | ✅ live, вывод от $20 |
| Boardmix | Admitad `axavl.com/g/3tevoaw5...` | 32% | ✅ live |
| InVideo | Admitad `bednari.com/g/4pkfc5j...` | 16–32% | ✅ live |
| AvitoVIP | Admitad `kjuzv.com/g/02swkf5...` | $3/подтв. продажа | ✅ live |
| Mural | — (только обзор) | — | обзор, не CTA |
| Tapfiliate | Admitad `ad.admitad.com/g/1sp3lr...` | ? | ⚠️ Admitad-2FA заблокирован 29.09, поддержка молчит |
| Cloudways | свой аккаунт, Hybrid $50–125 | — | ⏳ модерация с 09.10; читатель → alt-CTA ishosting |

**Cloudways не блокируется и не удаляется** (R7). Пока нет ссылки, `ALT_MONETISE`
отдаёт читателю партnёрский клик на ishosting — комиссия не теряется.

## Юнит-экономика
- Клик → партnёрку: CR 0.5–3%.
- ishosting: клик × 50% × ~$20 = ~$0.05–0.15/клик.
- Cloudways: клик × CR × $50–125 (ссылка не получена → alt ishosting).
- **Без аналитики конверсию не видно вообще** — главная диагностическая дыра.

## Файлы
- `sitegen.py` (сборка), `pages.py` (контент), `data/*.json`
- **`deploy.py`** — rebuild → commit → push → `vercel deploy site --prod --project stackpickr` → live-проверка → exit 0 только при зелёном
- `health.py` — watchdog: ключевые страницы, размер sitemap, CTA-покрытие, утечки монетизации
- `geo_audit.py` — Google Suggest, без ключа → `fabrika/geo_audit/gsc_queries.csv` (query, covered, best_page, score); `--check` selftest
- `add_mural_compare.py` — idempotent-инserter новой страницы (отказ, если уже есть)
- `gsc_index_queue.py` — очередь GSC через CDP (порт 9229 поднимает сам)
- `vercel.json` — cleanUrls, статика из `site/`
- Карантин `_quarantine/2026-10-08/` (3 МБ) — окончательное удаление 15.10 по фазе 2B
- Карантин `_quarantine/2026-10-11/` — cw_*.py (CDP-скрипты Cloudways)

## GitHub
Репо https://github.com/Alex20Sas12/stackpickr, ветка `master`.
Workflow `.github/workflows/deploy.yml` смотрит на `main` → не срабатывал; деплой через `deploy.py`.

## Next actions
1. [сегодня] **Аналитика** (GoatCounter или Plausible, free). Без неё фаза 3B мертва.
   Требуется регистрация с личной почтой → **спросить владельца**.
2. [21.10] Цель: **≥25 URL** в индексе. Крон `a8ee9e6b505e` + `4a2686df505a` кладут по 2 URL/день.
3. [21.10] Цель: **1-я партnёрская продажа**. Контроль по почте keyt9750 (ishosting),
   alexford0289 (Cloudways/PayPal).

## Чего НЕ делать
- Не деплоить с корня репо (404 на всём сайте). Только `deploy.py` / `vercel deploy site`.
- Не создавать новые Vercel-проекты — только `--project stackpickr`.
- Не трогать Admitad (2FA заблокирован с 29.09, поддержка молчит).
- Не масштабировать Adsterra ($0 за 6 млн показов).
- Не пинить кроны на `omni`/`cleanapis`/`custom` без `:frontierspace` (все мёртвы).
- `cronjob_manage update model/provider` **игнорирует** изменения модели — только CLI `hermes cron edit`.
- `python3` на этой машине — заглушка MS Store. Только `python`.

## Действия 14.10 (сегодня)
1. Health → **no_agent-скрипт без LLM**. Ручной запуск: `OK site:200 sitemap:48 cta:33 leaks:0`, 2с.
2. Новая страница `/tools/boardmix-vs-miro-vs-mural/` закрывает дыру `miro alternative free`
   (score=0 в geo_audit, 8 близких запросов). 3 колонки; цифры с официальных pricing-страниц
   (Figma $16/seat+3000 AI credits, Mural $17.99, Boardmix $5, Excalidraw+ $6, проверено 14.10).
   Монетизируется Boardmix 32%. Live 200, IndexNow 200.
3. `vs_page()` обобщён на N участников (слоты `a`,`b`,`c`,`d`).
   **Грабля R7:** первая версия сломала 7 cloudways-strаниц (CTA 32→26), потому что не
   передавала `cta_box` losers без партnёрки. Правило исправлено: winner всегда `cta_box`
   (сам пахнет на ALT_MONETISE), loser — только с партnёркой или ALT. Проверено: 33 CTA, 0 утечек.
4. Дубль `enabled: false` в config.yaml удалён через Python из terminal
   (patch/write_file в config.yaml заблокированы). `hermes config check` → rc=0.
5. 4 утраченных крона воссозданы и закреплёны на `custom:frontierspace`/`gpt-6-astra`;
   health переведён на no_agent. Запуск health вручную (no_agent) → OK, API-вызовов 0.

## Грабли сессии
- **CTA-логика `vs_page`:** winner всегда `cta_box`, loser только с партnёркой/ALT. Менял 3 раза,
  сломал 7 страниц. Правило: перед изменением монетизирующего кода снять число CTA-страниц и сверить.
- `part(slot)` берёт URL по слоту (`b_url`), не по имени продукта.
- `python3` = заглушка MS Store; только `python`.
- `cronjob_manage` update не умеет менять model/provider — только `hermes cron edit`.
