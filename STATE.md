# StackPickr (cmpsite) — State

## Проект
Статический сайт сравнений софта/хостинга с affiliate-монетизацией (Admitad) + Adsterra-реклама.
Домен: https://stackpickr.vercel.app (Vercel, статика, 40 страниц)

## Деньги (воронка)
- **Admitad affiliate**: Cloudways ($108), is*hosting (9-30%), Tapfiliate ($178), Boardmix (32%), InVideo (16-32%), AvitoVIP ($3)
- **Adsterra**: zone 6030096, NativeBanner_1 (1x4) — показы есть, $0 на балансе (низкий CPM RU-трафика)
- **AvitoVIP**: ДОБАВЛЕН 08.10.2026 — review + guide + hub /transfer/

## Критические проблемы (найдены 08.10)
| Проблема | Severity | Статус |
|----------|----------|--------|
| ~~Vercel-токены протухли (09.09)~~ | CRITICAL | ✅ ИСПРАВЛЕНО 08.10 21:50 — вход через email-код (keyt9750@gmail.com), деплой OK |
| Cloudways/is*hosting CTA → голые сайты без affiliate-ссылок | HIGH | Не исправлено (Admitad заблокирован 2FA, ждём support@mitgo.com) |
| ~~Навигация /tools/ → 404 на boardmix-vs-miro/mural, invideo-vs-canva~~ | HIGH | ✅ ЗАДЕПЛОЕНО 08.10 (3 новые страницы, 200 OK) |
| ~~AvitoVIP $3 не монетизировался (0 страниц)~~ | HIGH | ✅ ЗАДЕПЛОЕНО 08.10: /transfer/avitovip/ с kjuzv.com CTA + гайд + хаб |
| ~~Нет /privacy/~~ | MEDIUM | ✅ ЗАДЕПЛОЕНО |
| ~~Витринная ссылка → мёртвый shablony-pro.vercel.app~~ | MEDIUM | ✅ ЗАДЕПЛОЕНО (shablonypro.dpdns.org) |
| ~~SEO-backlog крон a7a4d645691d сломан (DSML-баг)~~ | MEDIUM | ✅ Пересоздан как content-крон cc9acb7a2028 |
| GSC-квота исчерпывается (общая ~10/день на все сайты) | LOW | Лимит 2/сайт/день соблюдается |

## Кроны
- GSC-крон 4a2686df505a: работает, ежедневно 10:10, сабмитит URL (квота ~2/сайт/день)
- SEO-backlog-крон a7a4d645691d: сломан (DSML), не выполняет backlog
- Дайджест ea6bf4fdb6cb: не работает (кронов нет в системе — потеряны при миграции)

## Файлы
- Код: cmpsite/sitegen.py + pages.py
- Данные: cmpsite/data/*.json
- Деплой: cmpsite/site/ → vercel --prod (требует auth)

## Следующие шаги (дедлайны)
1. [до 12.10] Admitad 2FA: проверить почту singap (himalaya envelope list --account singap | grep -i mitgo). При ответе — достать href Cloudways (id 23427) + is*hosting (id 173159) → вписать в data/config.json → пересборка → деплой (команда: `cd cmpsite/site && npx vercel@latest deploy --prod --yes`). До этого момента хостинг-CTA бесплатно рекламируют чужие сайты.
2. [10.10] Проверить GSC: появились ли новые URL (/transfer/*, /tools/*) в индексе после IndexNow-сабмита 08.10.
3. [ежедневно, content-крон] Триггер A1: новый запрос в geo_audit/gsc_queries.csv с impressions>=8 без страницы → создать страницу, пересборка, деплой, IndexNow.

## Автопилот (СОЗДАН 08.10)
| Крон | ID | Расписание | Что делает |
|------|----|-----------|-----------|
| health | 56d9c3299a42 | 8:00, 20:00 | сайт 200? sitemap >40? CTA не пустые? кроны не молчат? |
| content | cc9acb7a2028 | 9:00 | триггеры SEO-BACKLOG (A1: новый запрос impressions>=8 → страница) |
| traffic | d4bcf1a69171 | 12:00 | IndexNow новых URL + проверка GSC-крона |
| report | f22749669341 | 20:00 | вечерняя сводка (в сводку 20:00) |
- GSC-крон 4a2686df505a: работает, ежедневно 10:10 (квота 2/сайт/день)
- SEO-backlog a7a4d645691d: сломан DSML-багом 04.10 — пересоздан как content-крон выше

## GitHub
Репо: https://github.com/Alex20Sas12/stackpickr (создан 08.10, workflow .github/workflows/deploy.yml готов — нужен VERCEL_TOKEN secret после перелогина)
