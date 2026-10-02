/**
 * image-patch — draw viz figures as real terminal images in the transcript.
 *
 * Pi's supported Markdown transformer runs before layout and can only return
 * text, so it cannot reserve the rows an image needs. This wraps
 * `Markdown.prototype.render` the same way pi-math does: a `viz` fence becomes
 * a private-use marker line, the delegate lays the markdown out, then the
 * marker rows are swapped for the Kitty/iTerm2 image sequence. The wrapper is
 * installed once and delegates into whatever render is current, so pi-math's
 * own wrapper (which re-arms on turn start) stays in the chain.
 *
 * Everything is best-effort: without an image protocol or a working rasteriser
 * it returns the delegate's plain output and the ASCII transformer takes over.
 */
import { Markdown, allocateImageId, getCapabilities, renderImage } from "@earendil-works/pi-tui";
import { type Raster, rasterizeSpec } from "./raster.ts";
import { validateSpec } from "./spec.ts";

const FENCE_RE = /```viz[^\n]*\n([\s\S]*?)```/g;
const MARK_START = "\uE000";
const MARK_END = "\uE001";

const IMG_WIDTH_PX = 960;
const IMG_HEIGHT_PX = 520;

interface Placement {
  marker: string;
  raster: Raster;
}

const imageIds = new Map<string, number>();

function imageIdFor(key: string): number {
  let id = imageIds.get(key);
  if (id === undefined) {
    id = allocateImageId();
    imageIds.set(key, id);
  }
  return id;
}

function buildMarkers(source: string, frame: number): { text: string; placements: Placement[] } | undefined {
  const placements: Placement[] = [];
  let i = 0;
  const text = source.replace(FENCE_RE, (full, body: string) => {
    let parsed: unknown;
    try {
      parsed = JSON.parse(body.trim());
    } catch {
      return full;
    }
    const res = validateSpec(parsed);
    if (!res.ok) return full;
    const raster = rasterizeSpec(res.spec, { width: IMG_WIDTH_PX, height: IMG_HEIGHT_PX, frame });
    if (!raster) return full;
    const marker = `${MARK_START}${i}${MARK_END}`;
    i++;
    placements.push({ marker, raster });
    return `\n${marker}\n`;
  });
  if (placements.length === 0) return undefined;
  return { text, placements };
}

function imageBlock(placement: Placement, maxWidthCells: number): string[] | undefined {
  const caps = getCapabilities();
  if (!caps.images) return undefined;
  const result = renderImage(
    placement.raster.base64Data,
    { widthPx: placement.raster.widthPx, heightPx: placement.raster.heightPx },
    { maxWidthCells, maxHeightCells: 22, imageId: imageIdFor(placement.raster.base64Data.slice(-64)), moveCursor: false },
  );
  if (!result) return undefined;
  if (caps.images === "kitty") {
    return [result.sequence, ...Array.from({ length: result.rows - 1 }, () => "")];
  }
  const offset = result.rows - 1;
  const moveUp = offset > 0 ? `\x1b[${offset}A` : "";
  return [...Array.from({ length: offset }, () => ""), `${moveUp}${result.sequence}`];
}

function injectImages(lines: string[], placements: Placement[], maxWidthCells: number): string[] {
  const out: string[] = [];
  for (const line of lines) {
    const placement = placements.find((p) => line.includes(p.marker));
    if (!placement) {
      out.push(line);
      continue;
    }
    let block: string[] | undefined;
    try {
      block = imageBlock(placement, maxWidthCells);
    } catch {
      block = undefined;
    }
    if (block) out.push(...block);
    else out.push(line.replace(placement.marker, ""));
  }
  return out;
}

let installed = false;
let baseRender: ((this: unknown, width: number) => string[]) | undefined;
let wrapper: ((this: unknown, width: number) => string[]) | undefined;
const rendering = new WeakSet<object>();

function shouldHandle(source: unknown): boolean {
  return typeof source === "string" && source.includes("```viz") && !!getCapabilities().images;
}

/** Install the wrapper once, delegating into the render that is current now. */
export function installVizImagePatch(): void {
  if (installed) return;
  const proto = Markdown.prototype as unknown as { render: (this: unknown, width: number) => string[] };
  if (typeof proto.render !== "function") return;
  installed = true;
  baseRender = proto.render;

  wrapper = function (this: unknown, width: number): string[] {
    const md = this as { text?: string; paddingX?: number };
    const source = md.text;
    if (rendering.has(this as object) || !shouldHandle(source)) {
      return baseRender!.call(this, width);
    }
    rendering.add(this as object);
    let built: { text: string; placements: Placement[] } | undefined;
    try {
      const contentWidth = Math.max(20, width - (md.paddingX ?? 0) * 2);
      built = buildMarkers(source as string, 0);
      if (!built) return baseRender!.call(this, width);
      md.text = built.text;
      const lines = baseRender!.call(this, width);
      return injectImages(lines, built.placements, contentWidth);
    } catch {
      return baseRender!.call(this, width);
    } finally {
      if (built) md.text = source;
      rendering.delete(this as object);
    }
  };

  proto.render = wrapper as (this: unknown, width: number) => string[];
}

/** Restore the previous render. Safe to call when not installed. */
export function uninstallVizImagePatch(): void {
  if (!installed || !baseRender) return;
  const proto = Markdown.prototype as unknown as { render: unknown };
  if (proto.render === wrapper) proto.render = baseRender;
  installed = false;
  baseRender = undefined;
  wrapper = undefined;
  imageIds.clear();
}

export function vizImagePatchInstalled(): boolean {
  return installed;
}
