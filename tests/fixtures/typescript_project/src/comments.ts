/*
import { ghost } from "./missing";
export function Phantom() {}
*/

const example = `
export class TemplatePhantom {}
`;

const continued = "ignored\
export function StringPhantom() {}";

export interface VisibleShape {
  value: string;
}
