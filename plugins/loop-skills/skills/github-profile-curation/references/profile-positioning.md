# Profile positioning (README, pins, badges)

## Profile README

GitHub renders `README.md` from a repo named exactly like the username
(`USERNAME/USERNAME`, public) at the top of the profile page.

Create it:
```bash
mkdir profile && cp DRAFT.md profile/README.md && cd profile
git init -b main
git config user.name  "<personal name>"      # ensure the RIGHT identity
git config user.email "<personal email>"
git add README.md && git commit -m "Add profile README"
gh repo create USERNAME/USERNAME --public --source=. --remote=origin --push
```

### Deriving content from a CV
Map résumé sections to README sections:
- **Headline** ← the target positioning ("Generative AI Engineer · ML · Full-stack").
- **Bio** ← current role + what they build (1–3 sentences).
- **Skills** ← grouped tech stack (GenAI/LLM, ML/DS, languages, full-stack…).
- **Featured projects** ← flagship repos + live URLs (e-archeo style links).
- **Education / certifications** ← degrees + certs (e.g. IBM Data Science).

Always **show a draft and get approval before publishing**.

## Pinned repositories
There is **no API for pinning** — the user sets pins in the GitHub UI
("Customize your pins"). Recommend the 6 that best support the positioning,
ordered strongest-first. Lead with the ones that prove the target identity.

## Badges & stats — reliability matters

- **Reliable**: [shields.io](https://shields.io) static/dynamic badges
  (tech stack, `github/followers/<user>`), and komarev profile-view counter.
- **Flaky**: the shared `github-readme-stats.vercel.app` instance rate-limits on
  GitHub's API, so its cards intermittently render as **"Error Fetching
  Resource"** (via GitHub's `camo` image proxy). Don't rely on it for a profile
  you want to always look good.
- **Reliable stats card**: self-host `github-readme-stats` on the user's own free
  Vercel deployment with their token, then point the README at that instance.

Example reliable header:
```html
<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/github/followers/USERNAME?style=for-the-badge&logo=github&logoColor=white"/>
</p>
```

## Descriptions & topics
Fill missing repo `description` and `repositoryTopics` on showcased repos
(`gh repo edit OWNER/REPO --description "..." --add-topic ml,nlp`) — they improve
discoverability and how the profile scans.
