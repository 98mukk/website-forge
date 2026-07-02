# Apple.com live system — extracted from their real production CSS (Byakugan pass)

APPLE'S MOTION SIGNATURE: one workhorse easing curve used 78 times across the page: cubic-bezier(.4, 0, .6, 1) — a symmetric ease-in-out that feels calm and mechanical. A second curve, cubic-bezier(.25, .1, .3, 1) (fast start, long soft landing), is reserved for TRANSFORMS ONLY: nav slides, drawer movement, position changes. Two curves total for an entire flagship site. Restraint applies to motion, not just color.

APPLE'S DURATION SCALE: hover color changes are nearly instant at 20ms (feels like touching metal, not watching an animation); visibility and height transitions 240ms; transforms 300ms; opacity crossfades 320ms. Nothing on the page animates longer than ~350ms. Snappy micro, calm macro.

APPLE'S NAMED KEYFRAMES: every animation is named for its exact job (globalnav-chevron-hover-off, globalnav-flyout-slide-forward-next, globalnav-search-fade-and-slide-to-close). Forward and back get separate choreography. Nothing loops. Motion communicates state changes only: open, close, forward, back, focus.

APPLE'S FROSTED NAV RECIPE: fixed header ~48px tall, translucent dark background with backdrop-filter blur + saturate so content scrolls behind frosted glass, plus a full-screen scrim that fades in behind opened flyout menus. Depth from blur and tonal layers, never hard borders or drop shadows.

APPLE'S TYPE ARCHITECTURE: one superfamily split by size: SF Pro Display for large sizes (headlines), SF Pro Text for small sizes (body/captions) — same voice, optically tuned per size. Hierarchy comes from size + weight steps (weight 600 headlines, 400 body), never from color variety. Fallback stack always ends in system sans.

APPLE'S INTERACTION FEEL: hover states are near-instant (20ms) tonal shifts, not glows or lifts. Focus and open/close states get the slower 240-320ms choreography. The faster the feedback, the more physical the interface feels; the slower the transition, the more it reads as a spatial change.

APPLE'S RESTRAINT LAWS (from the full page scan): pure white or pure black page grounds with near-black/near-white text (#1d1d1f on #ffffff); exactly ONE accent (#0071e3 blue) appearing only on links and CTAs; pill buttons (radius 980px, 8px 15px padding); two-button hero pattern (filled primary + text-link secondary); massive whitespace; the product photography carries ALL the color while the UI stays silent.

APPLE'S PAGE RHYTHM: full-width stacked product tiles, alternating white and black backgrounds for rhythm; each tile holds one product, one headline (2 lines max), one subline, two CTAs, one hero image. Size = importance: flagship gets the full viewport, secondary products share a 2-up grid below.
