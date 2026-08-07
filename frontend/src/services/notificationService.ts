import apiClient from "@/lib/api";

export interface NotificationItem {
  id: string;
  user_id: string;
  title: string;
  message?: string;
  type: "info" | "warning" | "error" | "success" | string;
  category?: string;
  is_read: boolean;
  action_url?: string;
  created_at: string;
  updated_at: string;
}

export const notificationService = {
  getNotifications: async (params?: { unread_only?: boolean; category?: string }): Promise<NotificationItem[]> => {
    const response = await apiClient.get<NotificationItem[]>("/notifications", { params });
    return response.data;
  },

  markRead: async (notifId: string): Promise<NotificationItem> => {
    const response = await apiClient.patch<NotificationItem>(`/notifications/${notifId}/read`);
    return response.data;
  },

  markAllRead: async (): Promise<{ status: string; marked_count: number }> => {
    const response = await apiClient.post("/notifications/read-all");
    return response.data;
  },
};
