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
| Vercel-токены протухли (09.09) — деплой невозможен | CRITICAL | Ждём device-flow подтверждение владельца |
| Cloudways/is*hosting CTA → голые сайты без affiliate-ссылок | HIGH | Не исправлено (Admitad заблокирован 2FA) |
| Навигация /tools/ → 404 на boardmix-vs-miro/mural, invideo-vs-canva | HIGH | Исправлено в коде (3 новые страницы), ждёт деплоя |
| AvitoVIP $3 не монетизировался (0 страниц) | HIGH | Исправлено: review + guide + hub, ждёт деплоя |
| Нет /privacy/ (Adsterra требует) | MEDIUM | Исправлено в коде, ждёт деплоя |
| Витринная ссылка → мёртвый shablony-pro.vercel.app | MEDIUM | Исправлено на shablonypro.dpdns.org, ждёт деплоя |
| SEO-backlog крон a7a4d645691d сломан (DSML-баг) | MEDIUM | Требует проверки конфига |
| GSC-квота исчерпывается (общая ~10/день на все сайты) | LOW | Лимит 2/сайт/день соблюдается |

## Кроны
- GSC-крон 4a2686df505a: работает, ежедневно 10:10, сабмитит URL (квота ~2/сайт/день)
- SEO-backlog-крон a7a4d645691d: сломан (DSML), не выполняет backlog
- Дайджест ea6bf4fdb6cb: не работает (кронов нет в системе — потеряны при миграции)

## Файлы
- Код: cmpsite/sitegen.py + pages.py
- Данные: cmpsite/data/*.json
- Деплой: cmpsite/site/ → vercel --prod (требует auth)

## Следующие шаги
1. [СРОЧНО] Vercel device-flow: владелец открывает https://vercel.com/oauth/device?user_code=SGDP-FNCC → деплой 47 страниц
2. После деплоя: IndexNow сабмит новых URL (/transfer/, /privacy/, 3 новых vs)
3. Admitad 2FA: ждать ответ support@mitgo.com, потом подставить Cloudways/is*hosting affiliate-ссылки
4. Починить SEO-backlog крон (DSML → нормальный prompt)

## Автопилот (планируется)
- health: 2×/день — сайт 200, платёжка жива, кроны не молчат
- content: 1/день — новый vs/обзор/гайд по нише
- traffic: 1/день — IndexNow + GSC сабмит новых URL
- hunt: 2×/день — поиск заказов/баунти по профилю
- report: вечером — сводка
