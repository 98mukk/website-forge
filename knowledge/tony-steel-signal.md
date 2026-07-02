# Tony's Steel & Signal system (Truck League brand guidelines) — master-level design intel

TONY'S CORE THESIS: "Quiet steel until the league speaks." The resting UI is calm, cool, and tonal; the brand raises its voice (the one accent color) ONLY on live, lead, and win moments. Restraint = mastery. The accent means ONE thing, never decoration, never a fill, never a second meaning.

TONY'S ACCENT BUDGET LAW: on any single component, exactly ONE element may blaze in the hot accent; every other accent on that component drops to a quiet static tint with no glow. Hierarchy by intensity, not a flat ban. One primary CTA per screen. The accent is rationed like a scarce resource: highlight, never wallpaper.

TONY'S COLOR ARCHITECTURE: dark-mode-native gunmetal ladder. Surfaces climb tonal steps with NO borders: base #121519, card #191D22, modal #21262C, hover #2A3037. Hairline seams in rgba(220,228,235,0.07). Text: primary #EEF1F4 (16:1 AAA), secondary #A6AFB8, muted #717A83 (captions/units ONLY, never critical numbers). Accent family: static #FF6A2C, live #FF7A3D (AAA-gated), pressed #E85518, soft tint rgba(255,106,44,0.14). Secondary cyan #4FD0D8 is informational-only and always loses to the orange.

TONY'S CONTRAST GATES: body text must clear WCAG AA 4.5:1; safety-critical or hero values must clear AAA 7:1. He MEASURES every pairing and prints the ratio (e.g. accent-on-base 7.06:1 AAA). Muted text is fenced: 14px minimum, never carries a number a user must re-read. Contrast values are law, not aspiration.

TONY'S TYPOGRAPHY SYSTEM: Space Grotesk (500/700) for display and headings — engineered grotesque, reads as labelled equipment not marketing. IBM Plex Sans (400/500) body — large x-height for legibility in bad light. IBM Plex Mono (500/700) for ALL numerals with font-variant-numeric: tabular-nums so digit columns align. A fourth face (Chakra Petch) exclusively for the wordmark so the logo is its own object. BANNED FONTS: Inter, Roboto, Open Sans, Helvetica, Lato.

TONY'S TYPE SCALE: display 3.5rem/1.05 weight 700; h1 2.5rem/1.1; h2 1.75rem/1.15 weight 600; h3 1.25rem/1.2; body 1rem/1.6 weight 400; small 0.875rem/1.45; micro 0.75rem/1.35. Primary data numbers 18-28px, weight 500-700, tabular mono. Medium weights beat thin weights under glare.

TONY'S SPACING AND RADIUS TOKENS: spacing scale 4/8/12/16/24/32/48px. Radius system: cards 14px, buttons 12px, inputs 10px, small rows 8px, pills 9999px. Grid: 24-column subgrid, max content width 1280px (1440px for landing hero only). Decide once, obey everywhere.

TONY'S GRADIENT LAW: every gradient must do exactly ONE of four jobs: a mask (hold text contrast over imagery), a material (brushed-steel panel sheen), an instrument (gauge sweep, single readout glow), or a rationed seam (used max twice per page). A gradient that is none of these four is banned generic-dark-glow and gets rejected on sight. Never full-bleed glow.

TONY'S SIGNATURE GESTURE: "the single hot light" — exactly ONE radial accent glow per screen, placed behind the ONE critical value (the live rank, the key metric). Never multiplied. This one rationed glow is what makes the accent feel alive.

TONY'S MOTION SYSTEM: motion is instrument behavior, not animation — a gauge settling to its reading. Named easing tokens: settle cubic-bezier(0.2,0,0,1) for entrances/state changes (the default), ignite cubic-bezier(0.4,0,0.2,1) for win-moment fills, exit cubic-bezier(0.4,0,1,1) for dismissals. Durations: 120ms hover/press, 200ms state transitions, 300ms page transitions, 500ms progress fills. Browser default "ease" is banned. Win animations are one-shot, NEVER looping. Under prefers-reduced-motion every gesture renders at final state with no movement.

TONY'S COMPONENT STATE LAW: no component ships resting-state-only. Every interactive component defines default, hover, focus-visible, active/pressed, disabled, loading, error, and empty states. Buttons: hover lifts translateY(-1px) in 120ms, loading swaps label for an in-flight verb with inline spinner and no layout shift, disabled is tonal with muted label. Inputs: focus shows accent border PLUS a separate 2px cool a11y ring, error ties helper text via aria-describedby.

TONY'S FOCUS RING RULE: the keyboard focus indicator is a 2px high-contrast COOL ring with 2px offset — explicitly NOT the accent color, because the accent already has one meaning and focus would dilute it. Accessibility overrides mood: it is the one place the calm palette gives way.

TONY'S EMPTY-STATE DIGNITY RULE: an empty state is framed as a starting line, never a deficit. State the next concrete action ("No standing yet. Log your first trip to get on the board."), never mock the user or use cutesy apology. Empty states get the same design investment as win states.

TONY'S VOICE RULES: state the number, then stop — the fact is the message, the adjective is the oversell. Plain-professional formality, zero hype punctuation, no emoji, no exclamation inflation. Specific over salesy: name the real thing that happened ("$50 fuel card ready to redeem", not "Cha-ching!"). Errors are plain and actionable ("Couldn't load standings. Tap to retry."). Respect the reader as a professional.

TONY'S IMAGERY DIRECTION: photography carries the brand's warmth while the UI stays cool — the two never trade jobs. Subject on a third, NEVER dead-center (centered composition is the stock-photo default and is forbidden). The accent color must exist INSIDE the photography as a real light source (a tail light, a lamp, a streak) so brand color lives in the image itself. Motion in hero imagery by default: subject sharp, environment carries the blur. Low camera angle so the subject reads dominant. No faces — scenes and machines with silhouette presence. Cool shadows under warm light, no lifted blacks, no halation, no vintage grade.

TONY'S TEXTURE RULES: material treatments at very low opacity — steel sheen gradients, 4% hairline grids, one rare textural accent per page maximum. No two sections reuse the same texture treatment. Texture opacity creeping up (18%+) is how AI-slop returns. Elevation is tonal (lighter surface step), never drop shadows below 30% opacity.

TONY'S BANNED PATTERNS (rejected on sight): thin colored bars on dark cards; Inter/Roboto/Open Sans/Helvetica/Lato; faux-glass blur on cards; gradient text on heroes; cheap drop shadows; accent as wallpaper or full fill; skeuomorphism (faux bevels, embossed metal, glossy buttons); resting-state-only components; invisible or accent-colored focus rings; centered hero subject; a second loud accent competing with the primary; cartoonish/juvenile treatment (mascots, confetti, emoji-led copy, candy colors); rendering the wordmark as an image instead of live type.

TONY'S RESPONSIVE CONTRACT: phone-first (0-599px is the design default; everything else is progressive enhancement), tablet 600-1023px, desktop 1024px+ with max content 1280px. Components keep IDENTICAL anatomy and proportions across surfaces — a card never changes internal structure between phone and web, layouts only change density. Type in rem, scales to 200% with reflow, no hard-coded px on scalable text.

TONY'S TOUCH AND A11Y FLOORS: 44px minimum tap targets with 8px spacing; smaller visual elements carry invisible 44px hit areas. Color is never the sole signal — pair with symbol, label, or position. Real semantic HTML: tables for tabular data, aria-live for dynamic updates, focus trap in modals, logical heading order.

TONY'S PROCESS SIGNATURE: every major decision is backed by cited research (60 sources: WCAG specs, Apple HIG, NN/g studies, peer-reviewed color psychology). Decisions are written as laws with names ("The Seven Laws", "the accent budget", "the muted fence"), each with a one-line reason. A brand system defines what it is NOT (the positioning gate) as sharply as what it is.
