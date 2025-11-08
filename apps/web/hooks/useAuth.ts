import { useAuth as useClerkAuth, useUser } from '@clerk/nextjs';
import { useEffect } from 'react';
import { setAuthToken } from '@/lib/api';

export interface AuthUser {
  id: string;
  email: string | undefined;
  name: string | null;
  imageUrl: string | undefined;
}

export function useAuth() {
  const { userId, isLoaded, isSignedIn, getToken } = useClerkAuth();
  const { user } = useUser();

  // Automatically set auth token for API calls when token is available
  useEffect(() => {
    if (isLoaded && isSignedIn) {
      getToken().then((token) => {
        if (token) {
          setAuthToken(token);
        }
      });
    } else {
      setAuthToken(null);
    }
  }, [isLoaded, isSignedIn, getToken]);

  const authUser: AuthUser | null = user
    ? {
        id: userId!,
        email: user.primaryEmailAddress?.emailAddress,
        name: user.fullName,
        imageUrl: user.imageUrl,
      }
    : null;

  return {
    user: authUser,
    userId,
    isLoaded,
    isSignedIn,
    isAuthenticated: !!userId,
    getToken,
  };
}
