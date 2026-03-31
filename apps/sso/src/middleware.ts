import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { TRUSTED_CLIENTS } from './lib/trusted-clients';

function getTrustedClientOrigins(): string[] {
  const origins = new Set<string>();

  for (const client of TRUSTED_CLIENTS) {
    for (const redirectUrl of client.redirectUrls) {
      try {
        origins.add(new URL(redirectUrl).origin);
      } catch {
        // Ignore invalid URLs to avoid crashing middleware.
      }
    }
  }

  return Array.from(origins);
}

/**
 * CORS Middleware
 * 
 * Handles CORS for API routes dynamically based on request origin.
 * Only allows origins specified in ALLOWED_ORIGINS environment variable.
 * 
 * This is necessary because Next.js config headers() are static and can't
 * dynamically check the request origin.
 */
export function middleware(request: NextRequest) {
  // Only apply to API routes
  if (!request.nextUrl.pathname.startsWith('/api')) {
    return NextResponse.next();
  }

  // Get allowed origins from env + trusted OAuth client redirect URLs.
  // This prevents browser CORS failures during OAuth token exchange
  // when ALLOWED_ORIGINS isn't updated for a new client/app origin.
  const envAllowedOrigins =
    process.env.ALLOWED_ORIGINS?.split(',').map((origin) => origin.trim()) ||
    (process.env.NODE_ENV === 'development' ? ['http://localhost:3000'] : []);

  const trustedClientOrigins = getTrustedClientOrigins();
  const allowedOrigins = new Set<string>([
    ...envAllowedOrigins,
    ...trustedClientOrigins,
  ]);

  // Get the origin from the request
  const origin = request.headers.get('origin');

  // Check if origin is allowed and derive a non-null value for headers
  const isAllowedOrigin = !!origin && allowedOrigins.has(origin);
  const allowedOrigin = isAllowedOrigin && origin ? origin : null;

  // Create response
  const response = NextResponse.next();

  // Set CORS headers
  if (isAllowedOrigin && allowedOrigin) {
    response.headers.set('Access-Control-Allow-Origin', allowedOrigin);
    response.headers.set('Access-Control-Allow-Credentials', 'true');
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    response.headers.set(
      'Access-Control-Allow-Headers',
      'Content-Type, Authorization, X-Requested-With'
    );
    response.headers.set('Vary', 'Origin');
  }

  // Handle preflight OPTIONS request
  if (request.method === 'OPTIONS') {
    return new NextResponse(null, {
      status: 200,
      headers: response.headers,
    });
  }

  return response;
}

// Apply middleware to all API routes
export const config = {
  matcher: '/api/:path*',
};


