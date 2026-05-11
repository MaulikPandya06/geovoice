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
  selectedCountry: Country | null;
  selectedEvent: Event | null;
  setCountry: (c: Country) => void;
  setEvent: (e: Event) => void;
};

export const useGlobalStore = create<State>((set) => ({
  selectedCountry: null,
  selectedEvent: null,

  setCountry: (country) => set({ selectedCountry: country }),
  setEvent: (event) => set({ selectedEvent: event }),
}));