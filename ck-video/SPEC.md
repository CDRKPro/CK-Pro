GOAL:    l'artisan/commerçant se dit « je veux le même » et réserve un rendez-vous.
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps
TIME:    43.5 s x 30 = 1305 frames, music TBD (none yet)
LOOK:    ground #000000 (the site's own), cards #111113 with 2px gradient border, radius 32;
         gradient #38A8F5 -> #8E8CF6 -> #B98AF5 on ONE word per shot (the site's accent usage);
         display Syne 800, titles 100-112px, tracking -1%; body Bricolage Grotesque 400-500, 40-46px, grey #9A9AA0;
         icon squares = gradient tiles with black line icons (site's timeline); white pill buttons with black text.
OBJECTS: search bar, phone showing the real ckwebdesigner.fr hero, project rows (real client names),
         Google result card, map with pin, AI chat, notification feed, 4-step timeline, pricing bento, booking day chips.
MOTION:  enter expo.out / power4.out 0.5-0.7s; camera power2.inOut; exits power3.in 0.3s; words 70ms stagger blur 6px->0;
         rolling word = slot roll 0.35s; cursor 72px, click causes next state on same frame.
SHOTS:   S1 0-4.6 search typed, "Vos futurs clients vous cherchent en ligne." -> click -> blur swap
         S2 4.6-6.8 logo performed (speed dashes + chevrons) + wordmark, shrinks up (carry across)
         S3 6.8-11.6 "On crée la vitrine digitale" + phone rises with real site, scrolls; zoom-through exit
         S4 11.6-16.8 "Un site sur mesure / moderne / à votre image" over real project rows
         S5 16.8-22.4 "Visible sur Google / sur Maps / et même dans ChatGPT" three proof cards
         S6 22.4-26.4 "Vos visiteurs deviennent des clients" notification feed
         S7 26.4-30.8 "Un seul interlocuteur, du début à la fin" 4-step timeline lighting up
         S8 30.8-35.0 "On s'occupe de tout." bento, 599 € count-up
         S9 35.0-39.0 "Envie d'en faire autant ?" -> booking chips -> button click -> confirmé
         S10 39.0-43.5 logo end card, tagline, contact, service marquee
BANNED:  TikTok end card; invented testimonials or numbers; logo docked in a corner; everything fade+slide-up;
         text drifting after landing; glow orbs/particles.
QA:      0.0 (hook readable), 3.6 click, 6.0 lockup, 9.5 phone, 14, 20, 25, 29, 33, 37.5, 42.5.
