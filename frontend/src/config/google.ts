const DEFAULT_CLIENT_ID =
  "212233580664-j4diufuimp6qimk69sevf1km53oq1k1p.apps.googleusercontent.com";

export const GOOGLE_CLIENT_ID: string =
  (import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined)?.trim() ||
  DEFAULT_CLIENT_ID;

export const googleAuthEnabled = GOOGLE_CLIENT_ID !== "disabled";