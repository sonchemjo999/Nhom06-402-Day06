import { apiOk } from "@/lib/server/http";

export async function GET() {
  return apiOk({ status: "ok", ts: new Date().toISOString() });
}
