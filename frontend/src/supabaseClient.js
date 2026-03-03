/**
 * @fileoverview Supabase client singleton for auth and database access.
 */

import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing Supabase env: set REACT_APP_SUPABASE_URL and REACT_APP_SUPABASE_ANON_KEY in .env'
  );
}

/** Supabase client instance (auth + database). */
export const supabase = createClient(supabaseUrl, supabaseAnonKey);
