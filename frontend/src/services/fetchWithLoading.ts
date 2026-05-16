import { useGlobalStore } from "../store/useGlobalStore";

export async function fetchWithLoading(
  url: string,
  options?: RequestInit
): Promise<Response> {
  try {
    useGlobalStore.setState({ isLoading: true });
    const response = await fetch(url, options);
    return response;
  } finally {
    useGlobalStore.setState({ isLoading: false });
  }
}
