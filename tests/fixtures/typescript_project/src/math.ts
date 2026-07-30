export interface Calculator {
  add(left: number, right: number): number;
}

export type Numeric = number;

export enum Operation {
  Add = "add",
}

export function add(left: number, right: number): number {
  return left + right;
}
