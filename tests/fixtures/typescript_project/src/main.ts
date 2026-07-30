import type { Calculator } from "./math";
import { add } from "./math.js";
import React from "react";
export { Card } from "./components";

export const boot = (calculator: Calculator): number => calculator.add(1, add(2, 3));
