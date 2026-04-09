import { NextResponse } from "next/server";

export function apiOk<T extends Record<string, unknown>>(data: T, status = 200) {
  return NextResponse.json(data, { status });
}
