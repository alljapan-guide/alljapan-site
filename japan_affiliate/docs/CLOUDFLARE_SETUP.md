# Publishing on Cloudflare Pages (GitHub stays as storage and automation)

Order matters: keep the current GitHub Pages site live until the Cloudflare one works.
1. Cloudflare dashboard -> Workers & Pages -> Create -> Pages -> Upload assets. Name the project `alljapan`, upload `alljapan-site.zip`, deploy. Check https://alljapan.pages.dev (or the address shown).
2. In that project -> Custom domains -> add `alljapan.win`. Follow Cloudflare's prompts for the existing DNS records (remove the four GitHub A records and the `www` CNAME only when asked). Keep the Google TXT record.
3. Create an API token (My Profile -> API Tokens) that can edit Cloudflare Pages, and copy the Account ID (Workers & Pages overview). Check the exact permission names on the Cloudflare screen.
4. GitHub repo -> Settings -> Secrets and variables -> Actions: add secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` (add variable `CF_PAGES_PROJECT` only if the project is not named `alljapan`).
5. Re-run the workflow. When Cloudflare is configured it deploys there; GitHub Pages can then be unpublished (Settings -> Pages).
Docs: https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/
Limits: https://developers.cloudflare.com/pages/platform/limits/ (drag-and-drop 1,000 files; Wrangler/CI 20,000 files; 25 MiB per file).
