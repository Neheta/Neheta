# Pastel Pixel Profile: brand and setup guide

## Concept
A cozy indie-game title screen: a plum-black night sky, slowly drifting pastel petals,
a floating pixel cat, and a pixel typewriter. Every section is a "menu panel" with
stepped pixel corners. All motion is slow (4–24s loops, ease-in-out) and stops for
visitors who turn on "reduce motion".

## Brand tokens
| Token     | Hex       | Used for                                        |
|-----------|-----------|-------------------------------------------------|
| Background| `#1A1420` | banner, section headers, footer                 |
| Surface   | `#241B2E` | cards, badges, stats cards                      |
| Border    | `#3A2D45` | panel borders, dotted lines, empty meter cells  |
| Pink      | `#FFB3D1` | headings, name, key accents, snake              |
| Soft pink | `#F8C8DC` | typing line, petals                             |
| Blush     | `#FFD6E8` | cat, stars, glows                               |
| Rose      | `#D97AA5` | pixel drop shadows, sprite outlines             |
| Lavender  | `#C8B6FF` | small details only: ✦ markers, tags, plant      |
| Text      | `#EDE3F0` | body copy                                       |
| Muted     | `#A898B3` | secondary copy, meter labels                    |

**Rules**
- Pixel font (built in, 5×7) for headings, labels and the name. The system sans-serif font for sentences.
- Every panel uses the same stepped 4px pixel corner and a 2px `#3A2D45` border.
- Section headers always look like `✦ TITLE ········`.
- The logo mark (your initials in a stepped box) appears in the banner and the footer.
- Voice is lowercase and warm: "currently growing: rust".

**Alternate accents.** Set `"theme"` in `profile.json`:
- `"peach"`: peach-pink (`#FFC2A8`) with a pink accent
- `"rose-mint"`: the same pinks with a mint accent (`#A8E6CF`) instead of lavender

## Setup checklist
1. **Fill in `profile.json`.** Set your name, initials, GitHub username, role, bio, typing lines (30 characters max), stack, projects (2–4) and links.
   - Find stack logo slugs at simpleicons.org, e.g. `nodedotjs`.
2. **Build.** Run `python3 build.py`. It prints a note if any text was too long and got shortened.
3. **Preview locally.** Run `python3 -m http.server 8765` and open `http://localhost:8765/preview.html`.
4. **Create the repo.** On GitHub, create a **public** repo named exactly your username. GitHub shows a "special repository" notice when you get it right.
5. **Upload these files:**
   - `README.md`
   - `assets/` (all the SVGs)
   - `.github/workflows/snake.yml`
   - `profile.json` and `build.py` (required: the daily action uses them to draw your stats card)
   - Don't upload: `preview.html`, `preview/`, `.claude/`
6. **Turn on the daily action.**
   - In the repo, go to **Settings → Actions → General → Workflow permissions** and select **Read and write**.
   - Then go to **Actions → generate pink snake → Run workflow**. This creates an `output` branch with `stats.svg` and `snake-pink.svg` in it.
   - After that it refreshes daily.
7. **Check your profile page.** The animations play right on github.com.

## Notes
- **Stats card.** The popular `github-readme-stats.vercel.app` service is paused, so the daily action draws your stats card itself, in the brand's pixel style, using GitHub's own API. No third-party service is involved.
- **Streak card.** This comes from `streak-stats.demolab.com`, set to the brand colors.
- **Light mode.** Every panel carries its own dark background, so the branding stays the same when visitors use GitHub's light theme.
- **Accessibility.** Every image has alt text, and the about card's alt text holds its full content.
- **Rebuilding.** To change anything later, edit `profile.json` and run `python3 build.py` again. Don't hand-edit `README.md`.
