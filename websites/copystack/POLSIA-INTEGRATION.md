# CopyStack → Polsia: instrucțiuni de integrare

Acest pachet conține `index.html` — landing page-ul CopyStack complet, într-un
singur fișier autonom (HTML + CSS + JS inline, fără build step, fără librării).
Singura dependență externă este Google Fonts.

## Cum îl dai la Polsia

**Varianta recomandată (înlocuire completă):** atașează/lipește conținutul
`index.html` în chat-ul Polsia împreună cu promptul de mai jos.

---

### PROMPT DE COPIAT ÎN POLSIA

```
Replace my current website entirely with the single-file landing page I'm
providing below. Important rules:

1. Use the provided HTML/CSS/JS EXACTLY as given. Do not rewrite, "improve"
   or paraphrase the Romanian copy — it is final, including diacritics.
2. Keep everything in one page with the same section order:
   header → hero → marquee → problema → servicii (incl. the before/after
   slider) → proces (interactive timeline) → manifest → contact (WhatsApp
   qualifier chat) → footer.
3. The <script> block at the end is required — it powers: scroll progress,
   scroll reveals, count-up stats, the hero typewriter card with clickable
   tags, the draggable before/after slider (#ba-grab), the accordion
   timeline (#timeline), and the 6-question contact chat (#chat-body) that
   opens WhatsApp/email with prefilled answers. Include it unchanged.
4. Keep the Google Fonts <link> tags (Playfair Display, Inter, JetBrains
   Mono) in <head>.
5. Keep these real contact details exactly: amorosanu72@gmail.com and
   WhatsApp +40 741 672 024 (wa.me/40741672024).
6. If your platform requires splitting into components, split only on the
   section comments (<!-- ===== SECTION ===== -->) and keep all CSS
   selectors and element IDs intact (the JS targets them by ID).
7. Page language is Romanian: keep <html lang="ro"> and the meta
   description.

[PASTE THE FULL CONTENTS OF index.html HERE]
```

---

## Dacă Polsia integrează doar pe bucăți

Maparea către secțiunile existente ale site-ului tău:

| Secțiunea ta actuală | Înlocuiește cu (din index.html) | Marker |
|---|---|---|
| Hero "Cuvinte care chiar funcționează" | HERO + MARQUEE | `<!-- ===== HERO ===== -->` |
| "Problema / AI scrie rapid" | PROBLEMA (slop vs artizanat + comparativ + statistici) | `<!-- ===== PROBLEMA ===== -->` |
| "Ce construim / Întreaga stivă creativă" | SERVICII (6 carduri + slider Înainte/După) | `<!-- ===== SERVICII ===== -->` |
| "Cum funcționează / Trei pași" | PROCES (timeline interactiv, 6 pași) | `<!-- ===== PROCES ===== -->` |
| "Brandul tău merită copy..." | MANIFEST | `<!-- ===== MANIFEST ===== -->` |
| "Hai să vorbim" | CONTACT (chat calificare WhatsApp) | `<!-- ===== CONTACT ===== -->` |

Reguli la integrarea pe bucăți:
- **CSS:** copiază TOT blocul `<style>` o singură dată (tokens în `:root` +
  stilurile tuturor secțiunilor). Nu redenumi clase.
- **JS:** copiază TOT blocul `<script>` o singură dată, la finalul paginii.
  Fiecare comportament își caută singur elementele și se dezactivează dacă
  secțiunea lipsește, deci scriptul e sigur chiar și cu secțiuni parțiale.
- **ID-uri obligatorii** (JS-ul le caută): `header`, `hero-title`,
  `forge-out`, `forge-type`, `forge-tags`, `timeline`, `ba`, `ba-frame`,
  `ba-grab`, `ba-divider`, `chat-body`, `chat-prog`.

## Detalii tehnice pe scurt

- **Design tokens** în `:root`: fundal `#0d0c0a→#0a0908`, text `#f4efe6`,
  accent chihlimbar `#f5a623`, borduri hairline `rgba(255,255,255,.09)`.
- **Fonturi:** Playfair Display 900 (titluri), Inter (text), JetBrains Mono
  (etichete uppercase).
- **Responsive:** mobile-first; testat logic pe 375/768/1024/1440. Nav
  link-urile se ascund sub 760px (CTA rămâne).
- **Accesibilitate:** skip-link, focus rings, ținte tactile ≥44px,
  `prefers-reduced-motion` respectat peste tot, aria pe slider/acordeon/chat.
- **Slider-ul Înainte/După** folosește unități container-query (`cqw`) —
  suportate în toate browserele din 2023+.
