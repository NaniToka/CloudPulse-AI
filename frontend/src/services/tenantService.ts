/**
 * Frontend Service Client for Multi-Tenant Enterprise SaaS
 */

import apiClient from "@/lib/api";
import type {
  Organization,
  Team,
  Project,
  OrganizationMember,
  Invitation,
  AuditLog,
  PermissionMatrix,
} from "@/types/tenant";

export const tenantService = {
  async getOrganizations(): Promise<Organization[]> {
    const response = await apiClient.get<Organization[]>("/organizations");
    return response.data;
  },

  async createOrganization(name: string, plan: string = "Enterprise"): Promise<Organization> {
    const response = await apiClient.post<Organization>("/organizations", { name, plan });
    return response.data;
  },

  async getOrganization(orgId: string): Promise<Organization> {
    const response = await apiClient.get<Organization>(`/organizations/${orgId}`);
    return response.data;
  },

  async getAuditLogs(orgId: string): Promise<AuditLog[]> {
    const response = await apiClient.get<AuditLog[]>(`/organizations/${orgId}/audit-logs`);
    return response.data;
  },

  async getTeams(orgId: string): Promise<Team[]> {
    const response = await apiClient.get<Team[]>("/teams", { params: { organization_id: orgId } });
    return response.data;
  },

  async createTeam(orgId: string, name: string, description?: string): Promise<Team> {
    const response = await apiClient.post<Team>("/teams", { organization_id: orgId, name, description });
    return response.data;
  },

  async getProjects(orgId: string): Promise<Project[]> {
    const response = await apiClient.get<Project[]>("/projects", { params: { organization_id: orgId } });
    return response.data;
  },

  async createProject(orgId: string, name: string, cloudProvider: string = "AWS", environment: string = "Production"): Promise<Project> {
    const response = await apiClient.post<Project>("/projects", {
      organization_id: orgId,
      name,
      cloud_provider: cloudProvider,
      environment,
    });
    return response.data;
  },

  async getMembers(orgId: string): Promise<OrganizationMember[]> {
    const response = await apiClient.get<OrganizationMember[]>("/members", { params: { organization_id: orgId } });
    return response.data;
  },

  async inviteMember(orgId: string, email: string, role: string): Promise<Invitation> {
    const response = await apiClient.post<Invitation>("/members/invite", {
      organization_id: orgId,
      email,
      role,
    });
    return response.data;
  },

  async getPermissionsMatrix(): Promise<PermissionMatrix> {
    const response = await apiClient.get<PermissionMatrix>("/members/permissions");
    return response.data;
  },
};
