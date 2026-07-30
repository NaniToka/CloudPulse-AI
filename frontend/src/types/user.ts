export interface User {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  role: string;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  organization_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserProfile extends User {
  organization_name: string | null;
}
