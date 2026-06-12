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
Replace my current LANDING PAGE with the single-file page I'm providing
below. My site also has an existing, working GENERATOR tab — that one must
stay exactly as it is. Important rules:

1. DO NOT TOUCH THE GENERATOR. My Generator tab/page and its script already
   work. Do not replace, rewrite, restyle or merge its script with the new
   code. The file I'm giving you is ONLY the landing page.
2. Wire the two "Încearcă Generatorul" buttons (one in the sticky header,
   one in the hero) to my existing Generator tab's route. They currently
   have href="/generator" as a placeholder — swap in the real route. There
   are HTML comments marking both spots ("POLSIA: înlocuiește href...").
3. The "Forja AI în acțiune" card in the hero is a decorative typewriter
   DEMO, not the real generator. Keep it as-is alongside the real Generator
   tab — they serve different purposes (the card teases, the tab delivers).
4. Use the provided HTML/CSS/JS EXACTLY as given. Do not rewrite, "improve"
   or paraphrase the Romanian copy — it is final, including diacritics.
5. Keep everything in one page with the same section order:
   header → hero → marquee → problema → servicii (incl. the before/after
   slider) → proces (interactive timeline) → manifest → contact (WhatsApp
   qualifier chat) → footer.
6. The <script> block at the end of the landing page is required — it
   powers: scroll progress, scroll reveals, count-up stats, the hero
   typewriter card with clickable tags, the draggable before/after slider
   (#ba-grab), the accordion timeline (#timeline), and the 6-question
   contact chat (#chat-body) that opens WhatsApp/email with prefilled
   answers. Include it unchanged. It is scoped to the landing page only
   and will not conflict with the Generator's script.
7. Keep the Google Fonts <link> tags (Playfair Display, Inter, JetBrains
   Mono) in <head>.
8. Keep these real contact details exactly: amorosanu72@gmail.com and
   WhatsApp +40 741 672 024 (wa.me/40741672024).
9. If your platform requires splitting into components, split only on the
   section comments (<!-- ===== SECTION ===== -->) and keep all CSS
   selectors and element IDs intact (the JS targets them by ID).
10. Page language is Romanian: keep <html lang="ro"> and the meta
    description.
11. On the Generator tab, you may apply ONLY the visual theme so it matches
    the landing page (colors, fonts from the design tokens listed below) —
    but never change its logic, script or functionality. If in doubt, leave
    the Generator completely untouched.

[PASTE THE FULL CONTENTS OF index.html HERE]
```

---

## Tab-ul Generator (există deja — NU se înlocuiește)

Generatorul tău de pe Polsia funcționează deja și are propriul script.
Reguli pentru integrare:

- **Scriptul generatorului rămâne neatins.** Landing page-ul nu conține și
  nu are nevoie de niciun cod de generator. Scriptul landing-ului e izolat
  (un IIFE care își caută elementele după ID) și nu intră în conflict cu el.
- **Legătura dintre landing și generator:** cele două butoane "Încearcă
  Generatorul" (header + hero) au `href="/generator"` ca placeholder, cu
  comentarii HTML care marchează locul. Polsia trebuie doar să pună ruta
  reală a tab-ului.
- **Cardul "Forja AI în acțiune" din hero NU e generatorul** — e o
  demonstrație vizuală (typewriter cu exemple fixe) care face teasing spre
  generatorul real. Se păstrează amândouă.
- **Opțional, doar vizual:** generatorul poate primi tema landing-ului ca să
  arate unitar — tokens din `:root`: fundal `#0d0c0a`, text `#f4efe6`,
  accent `#f5a623`, fonturi Playfair Display / Inter / JetBrains Mono,
  butoane pill cu gradient amber. Logica și scriptul lui rămân exact cum sunt.
- **Opțional, dacă generatorul suportă parametri:** tag-urile din cardul
  Forja (Ad Copy / Landing Page / Email / Brand Voice) pot deveni link-uri
  către generator cu tipul preselectat (ex: `/generator?tip=email`). Doar
  dacă generatorul citește deja un asemenea parametru — altfel lasă-le cum sunt.

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
