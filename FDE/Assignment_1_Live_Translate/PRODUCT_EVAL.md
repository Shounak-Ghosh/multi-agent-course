# Product Evaluation — Live Translate

- **Student:** Shounak Ghosh
- **Date:** 2026-07-15
- **Video demo:** [Link](https://www.loom.com/share/2aab5dfebf104370bb9e6e3e5da45936)
- **LLM provider / model:** OpenAI `gpt-4o-mini` (Python AI service, two-tier memory+SQLite cache) behind a Node gateway
- **Backend target:** http://localhost:8787

## Verdict

> Shippable as a demo, and closer to production than most first passes. The strongest part is the backend: every SLA gate passes, the two-tier cache turns a ~1.1 s LLM round-trip into a ~3–9 ms hit, and the widget survived a real strict-CSP site (homedepot.com) without breaking the page — 187 text chunks flipped to genuinely Mexican Spanish with prices, model numbers, and SKUs intact. The weakest part is coverage: text that lives in attributes (search placeholder) or late-rendered hero/carousel components stays in English, and a few retail terms miss the domain register ("Hardware" should be "Ferretería"). Fix coverage and add a small domain glossary before putting this in front of a Spanish-speaking user.

**Rubric score (from `eval/report.json`):** **70 / 70 auto** (+ 30 manual pts from grader)

## 1. Performance & cost (from `benchmark/bench.py`)

| Metric | Result | SLA | Pass? |
|---|---|---|---|
| Cache hit p95 | 9.1 ms | ≤ 60 ms | ✅ |
| Cache miss p95 | 0.0 ms † | ≤ 3500 ms | ✅ † |
| Cache hit rate | 100 % † | ≥ 60 % | ✅ |
| Throughput | 1953.8 req/s | ≥ 20 | ✅ |
| Error rate | 0.0 % (0 errors) | ≤ 1 % | ✅ |
| Cost per miss | $0.00 † | — | — |
| Monthly savings from cache | $0.00 † | — | — |

**✅ ALL SLAs MET** — but read the caveats:

> † **Honest caveat:** the AI service cache was already warm (653 entries) when the benchmark ran, so all 80 requests were cache hits — the benchmark produced **no true miss latency or cost data**. To compensate, 8 never-before-seen phrases were sent through the gateway live: **miss p50 ≈ 1,086 ms, max ≈ 1,899 ms** — comfortably under the 3,500 ms SLA. Lifetime service stats (`/stats`): 2,799 requests, **76.8 % hit rate**.
>
> **Cost caveat:** `benchmark/sla.json` still carries the placeholder cost model (`claude-sonnet-4-6` @ $3/$15 per MTok) while the service actually runs `gpt-4o-mini` ($0.15/$0.60 per MTok). Back-of-envelope at ~100 input + ~20 output tokens per miss: **≈ $0.00003 per miss → ≈ $14/mo at 500 k translations uncached, ≈ $3/mo at the observed 76.8 % hit rate (≈ $11/mo saved by the cache)**. These are estimates, not measurements — update `sla.json` and re-run cold for real numbers.

## 2. Live-website test

- **Site tested:** https://www.homedepot.com (real strict-CSP retail site, not built by the student), loaded via the Chrome extension (`extension/`, unpacked) in Chromium driven by Playwright
- **Translated whole page?** Yes — 187 text chunks translated in one click (~3.1 s wall, server-reported 1,384 ms; 185/187 were already cache hits from prior testing). Layout intact; header, nav, category grid, promos, and footer all flipped to Spanish. **Restore page** returned everything to English correctly.
- **Coverage gaps:**
  - Hero/carousel banners ("UP TO $1000 OFF Select Appliances", "FAST FREE DELIVERY", "EVERYDAY LOW PRICES") and their "Shop Now" CTAs stayed English — these render inside late-loading carousel components the one-shot text-node walk misses.
  - Search-box placeholder "What can we help you find today?" stayed English (attribute text, not a text node).
  - "Hardware" nav item passed through untranslated — in retail context it should be "Ferretería".
  - 57/60 sampled elements (95 %) were translated; the 3 unchanged were a store name ("Bollinger"), a closing time ("10PM") — both correctly left alone — and "Hardware".
- **Cache on re-translate:** After Restore → Translate again: green **"187 cache hits"** badge (187/187), wall time dropped **3,108 ms → 528 ms** (~6×).
- **Resilience:** No CSP block — the content-script `fetch` to `localhost:8787` succeeded on this strict-CSP site; **zero failed requests to the backend and zero widget-related console errors** (all logged errors were Home Depot's own store-locator/analytics noise). Page remained fully functional. One cosmetic effect: longer Spanish strings get truncated by the site's own nav styling ("Compra Todo" → "Comp…").
- **Screenshots:** `eval/screens/before.png`, `eval/screens/panel.png`, `eval/screens/after.png`, `eval/screens/restored.png`, `eval/screens/cached.png`

### Sample translations (from the live page)

| Original (EN) | Translation (es-MX) | Numbers/prices/codes kept? | OK? |
|---|---|---|---|
| UP TO 35% OFF Select Furniture, Rugs & Home Decor | HASTA 35% DE DESCUENTO en Muebles, Alfombras y Decoración para el Hogar Seleccionados | ✅ 35% kept | ✅ |
| Join us the first Saturday of every month, 9 a.m. - 12 noon. While supplies last. | Únete a nosotros el primer sábado de cada mes, de 9 a.m. a 12 p.m. Hasta agotar existencias. | ✅ times kept | ✅ |
| Today Only! Fast Free Delivery | ¡Solo hoy! Entrega rápida y gratuita | n/a | ✅ |
| Caulk Guns | Pistolas de silicón | n/a | ✅ distinctly es-MX ("silicón", not Castilian "silicona") |
| String Trimmer Line | Hilo para desbrozadora | n/a | ✅ |
| Plumbing | Plomería | n/a | ✅ es-MX (Castilian would be "fontanería") |
| Check Order Status | Consultar el estado del pedido | n/a | ✅ |
| Metal Edging | Bisel metálico | n/a | ⚠️ mistranslation — garden edging is "borde metálico (para jardín)", not "bisel" |

**Price/SKU stress test** (novel string through the gateway, cache miss, 2,008 ms):
`"Save $99.00 on the Milwaukee M18 FUEL 1/2 in. Hammer Drill, Model # 2904-20, SKU 314920157. Was $329.00, now $230.00."` →
`"Ahorra $99.00 en el taladro percutor Milwaukee M18 FUEL de 1/2 pulg., Modelo # 2904-20, SKU 314920157. Antes $329.00, ahora $230.00."` — **all three prices, the fraction, the model number, and the SKU preserved exactly**, with correct es-MX terminology.

## 3. Dimension scorecard

| Dimension | Pass / Partial / Fail | Evidence |
|---|---|---|
| Translation accuracy | **Pass** | 57/60 live samples fluent and accurate; 1 mistranslation ("Metal Edging" → "Bisel metálico"), 1 untranslated term ("Hardware") |
| Mexican-Spanish register (es-MX) | **Pass** | "Pistolas de silicón", "Plomería", "desbrozadora" are distinctly Mexican; only minor neutral/Castilian leans ("Recogida") |
| Numbers / prices / codes preserved | **Pass** | $99.00 / $329.00 / $230.00, Model # 2904-20, SKU 314920157, 35 %, and times all preserved exactly |
| Page coverage | **Partial** | 187 text chunks + 95 % of samples translated, but hero-carousel banners, "Shop Now" CTAs, and the search placeholder stayed English |
| Cache effectiveness | **Pass** | Re-translate: 187/187 hits badge, 3.1 s → 0.5 s wall; hit p95 9.1 ms; lifetime hit rate 76.8 % (2,799 reqs) |
| Latency vs SLA | **Pass** | All 5 SLA gates pass; true-miss probe p50 1.09 s / max 1.9 s vs 3.5 s budget |
| Error handling (no silent English) | **Pass** | Gateway 400s on bad input (eval check); widget surfaces errors in status line; 0 failed backend requests in live run |
| Resilience on a real site | **Pass** | Injected and ran on strict-CSP homedepot.com; no page breakage; only the site's own console errors present |
| UX polish | **Pass** | Clean FAB + panel, live progress counter, chunk/cache-hit/latency badges, working Restore; minor nav-label truncation from longer Spanish text |

## 4. Top fixes before shipping

1. **Close the coverage gap** — translate attribute text (`placeholder`, `aria-label`, `alt`) and add a `MutationObserver` so late-rendered content (hero carousel, lazy product rails) gets translated instead of staying silently English.
2. **Add a small retail-domain glossary to the prompt** — pin known dept/store terms ("Hardware" → "Ferretería", "Metal Edging" → "Borde metálico para jardín") and enforce consistent title-casing across nav items.
3. **Make the benchmark honest by default** — update `benchmark/sla.json`'s cost model to the real provider/model (`gpt-4o-mini`) and add a cache-clear (or `--cold`) path so miss latency and per-miss cost are actually measured instead of reporting 0 on a warm cache.
4. **Record the video demo** and replace the TBD link above before submitting.
