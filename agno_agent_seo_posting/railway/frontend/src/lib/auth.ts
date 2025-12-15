import { betterAuth } from "better-auth";
import { Pool } from "pg";

// Create PostgreSQL pool using DATABASE_URL from environment
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const auth = betterAuth({
  database: pool,
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day - update session if older than 1 day
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },
  user: {
    additionalFields: {
      role: {
        type: "string",
        defaultValue: "user",
      },
    },
  },
  trustedOrigins: [
    process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  ],
});

// Export types for use in other files
export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
