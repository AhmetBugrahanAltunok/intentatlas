import { add } from "./math";

export function verifiesAdd(): boolean {
  return add(2, 3) === 5;
}
