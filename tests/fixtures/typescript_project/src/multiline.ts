import {
  Card,
} from "./components";

export function createCard(title: string): Card {
  return new Card(title);
}
