# Review — CK Web Designer promo v2 (9:16, 44.4 s)

- v2 rebuilt to match the reference's staging (user: "ça ressemble pas"): night ground #07080D with two large arcs,
  3D field of the site's own pages (S1, S4), lighter Syne 600 titles with a tiny letter-spaced label, accent letters dropping in,
  phone rising in 3D with a real scroll (S3, S9), pages whipping in tilted per word (S4), hub with orbiting icons + cards (S5),
  continuous notification feed (S6), quote card + "1 seul interlocuteur" + 4-step line instead of the testimonial (S7),
  depth-of-field pass then bento assembles (S8), glowing pill CTA with click (S9), logo end card with marquee (S10).
- Kept: CK colours (gradient #38A8F5 -> #B98AF5), official animated logo (assets/logo-anime.webm), real copy and prices.
- Featured pages in S4 are ckwebdesigner.fr pages (no client-site screenshots available yet).
- Warnings kept: film_silent (no music yet), per-letter titles counted as words, feed rows scrolling past (decorative), mini brand tag in S3.
- Edit copy/timings in build.py, then `python3 build.py`.

## Voix off (v3)
- Source: ElevenLabs Voice Design preview sent by Cédric (screen recording), audio only. It paraphrases the script (51 s).
- Cut "Bonjour à tous." and "on va parler de quelque chose de super important pour votre business,"; gaps tightened; 13 pieces placed in assets/vo.wav (46.7 s), -16 LUFS, peak -2.4 dBFS.
- Scenes retimed to the voice (film now 46.7 s); S9 on-screen text changed to "Prêt à passer au niveau supérieur ?" to match the voice.
- Checked by re-transcribing the rendered file (Whisper small, local): every line present, in order. Measured, not heard.
- Still no music bed.
