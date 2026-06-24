/**
 * bks-account-redirect
 * Intercetta account.bakabo.club e reindirizza verso il pannello BKS Members.
 * Lascia passare SOLO il flusso di autenticazione Shopify.
 */
export default {
  async fetch(request) {
    const url  = new URL(request.url);
    const path = url.pathname;

    // Lascia passare: flusso OAuth / login / callback / asset statici / API
    const passthrough =
      path.startsWith("/authentication") ||
      path.startsWith("/account/oauth")  ||
      path.startsWith("/cdn-cgi/")       ||
      path.includes("/callback")         ||
      path.includes(".js")               ||
      path.includes(".css")              ||
      path.includes(".woff")             ||
      path.includes(".png")              ||
      path.includes(".jpg")              ||
      path.includes(".svg")              ||
      request.method !== "GET";

    if (passthrough) return fetch(request);

    // Tutte le altre GET con HTML (ordini, profilo, root) → BKS Members
    const accept = request.headers.get("accept") || "";
    if (accept.includes("text/html")) {
      return Response.redirect("https://bakabo.club/pages/bks-members", 302);
    }

    return fetch(request);
  },
};
