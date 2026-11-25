// Entry for make.fun "Convince the AI Judge to Visit Your House: A Letter in One Image".
//
// The entry is a single image: a warm letter inviting the AI judge to a
// "Comfort & Cookies" evening at the writer's house. The image is built
// ahead of time (AI-generated cozy-room header + typeset letter) and shipped
// in this repository as entry.png. This program only copies that committed
// image to /output/entry.png, so the grader sandbox needs nothing beyond
// Node itself: no network, no image libraries, no build tools.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = "/output";

if (!existsSync(source)) {
  throw new Error(`missing committed image: ${source}`);
}
mkdirSync(outDir, { recursive: true });
copyFileSync(source, join(outDir, "entry.png"));
console.log("wrote /output/entry.png");
