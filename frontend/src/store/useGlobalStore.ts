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

  setEvent: (event: Event) => void;
  setCountry: (country: Country | null) => void;
};

export const useGlobalStore = create<State>((set) => ({
  selectedEvent: null,
  selectedCountry: null,

  setEvent: (event) =>
    set({
      selectedEvent: event,
      selectedCountry: null,
    }),

  setCountry: (country) =>
    set({
      selectedCountry: country,
    }),
}));