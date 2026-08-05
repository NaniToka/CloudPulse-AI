/**
 * TypeScript Type Definitions for Multi-Tenant SaaS Architecture
 */

export interface Organization {
  id: string;
  name: string;
  slug: string;
  logo?: string;
  logo_url?: string;
  plan: "Free" | "Pro" | "Enterprise";
  status: "Active" | "Suspended";
  owner_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Team {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  created_at: string;
}

export interface Project {
  id: string;
  organization_id: string;
  team_id?: string;
  name: string;
  cloud_provider: "AWS" | "GCP" | "Azure";
  environment: "Production" | "Staging" | "Development";
  region: string;
  created_at: string;
}

export interface OrganizationMember {
  id: string;
  organization_id: string;
  user_id: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  role: "Owner" | "Admin" | "Manager" | "Engineer" | "Viewer";
  created_at: string;
}

export interface Invitation {
  id: string;
  organization_id: string;
  email: string;
  role: string;
  token: string;
  status: "Pending" | "Accepted" | "Expired" | "Revoked";
  created_at: string;
}

export interface AuditLog {
  id: string;
  organization_id: string;
  user_id?: string;
  action: string;
  details: Record<string, any>;
  created_at: string;
}

export type PermissionMatrix = Record<string, string[]>;
