type PrismaClientAny = any;

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClientAny | undefined;
};

export async function getPrisma(): Promise<PrismaClientAny> {
  if (globalForPrisma.prisma) {
    return globalForPrisma.prisma;
  }

  const mod = await import("@prisma/client");
  const PrismaClient = mod.PrismaClient as new (options?: unknown) => PrismaClientAny;

  const client = new PrismaClient({ log: ["error"] });
  if (process.env.NODE_ENV !== "production") {
    globalForPrisma.prisma = client;
  }

  return client;
}
