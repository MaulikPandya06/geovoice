import { create } from "zustand";

type Country = {
  id: string;
  name: string;
};

type Event = {
  id: number;
  title: string;
};

type State = {
  selectedEvent: Event | null;
  selectedCountry: Country | null;
  isLoading: boolean;

  setEvent: (event: Event) => void;
  setCountry: (country: Country | null) => void;
  setLoading: (loading: boolean) => void;
};

export const useGlobalStore = create<State>((set) => ({
  selectedEvent: null,
  selectedCountry: null,
  isLoading: false,

  setEvent: (event) =>
    set({
      selectedEvent: event,
      selectedCountry: null,
    }),

  setCountry: (country) =>
    set({
      selectedCountry: country,
    }),
  setLoading: (loading) =>
    set({
      isLoading: loading
    }),
}));