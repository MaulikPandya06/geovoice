// hooks/useEvents.ts
import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";

export const useEvents = () =>
  useQuery({
    queryKey: ["events"],
    queryFn: async () => {
      const res = await api.get("/events/");
      return res.data;
    },
  });
