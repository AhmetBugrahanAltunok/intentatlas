import { boot } from "./main";

export const verifiesBoot = (): boolean => boot({ add: (left, right) => left + right }) === 6;
