# steps/D_footer_cek/step.py
from __future__ import annotations

from pathlib import Path

from pipeline.types import Context, FooterGate, FooterDecision
from .config import FooterCekConfig
from .service import FooterCekService


def _find_tile_for_emiten(tiles_dir: Path, emiten: str) -> Path | None:
    patterns = [f"*_{emiten}.png", f"*_{emiten}.jpg", f"*_{emiten}.jpeg"]
    for pat in patterns:
        matches = list(tiles_dir.glob(pat))
        if matches:
            return max(matches, key=lambda p: p.stat().st_mtime)
    return None


def _derive_tiles_dir_from_ctx(ctx: Context) -> Path | None:
    """
    Ambil folder Tiles berdasarkan lokasi raw capture:
    .../output/images/<DATE>/Raw/<raw>.png  -> .../output/images/<DATE>/Tiles
    """
    raw_path = getattr(ctx, "raw_path", None) or getattr(ctx, "raw_latest_path", None)
    if not raw_path:
        raw_path = getattr(ctx, "raw_latest", None)

    if not raw_path:
        return None

    p = Path(raw_path)
    if p.exists() and p.parent.name.lower() == "raw":
        return p.parent.parent / "Tiles"
    return None


def jalankan_step_D_footer_cek(ctx: Context) -> Context:
    cfg = FooterCekConfig()
    svc = FooterCekService(bin_threshold=cfg.bin_threshold)

    raws = svc.run(ctx.footer_cek_items)

    # Debug Tiles (fallback). Saat ini ctx.raw_path memang belum ada -> tiles_dir None.
    tiles_dir = _derive_tiles_dir_from_ctx(ctx)
    if tiles_dir:
        print(f"[D_footer_cek][debug] tiles_dir={tiles_dir} exists={tiles_dir.exists()}")
    else:
        print("[D_footer_cek][debug] tiles_dir=None (raw_path tidak ditemukan di context)")

    # Fallback: kalau tidak ada % dan belum NOT_AVAILABLE, coba baca tile file jika ada.
    patched = []
    for r in raws:
        if (not r.has_percent) and (not r.is_not_available):
            tile_path = None
            if tiles_dir and tiles_dir.exists():
                tile_path = _find_tile_for_emiten(tiles_dir, r.emiten)

            print(f"[D_footer_cek][debug] emiten={r.emiten} has_percent={r.has_percent} tile_path={tile_path}")

            if tile_path:
                ok, text = svc.detect_not_available_from_tile_path(tile_path, return_text=True)
                print(f"[D_footer_cek][debug] emiten={r.emiten} not_available={ok} tile_ocr='{text}'")
                if ok:
                    r = type(r)(
                        emiten=r.emiten,
                        has_percent=False,
                        is_not_available=True,
                        raw_text=(r.raw_text or ""),
                    )
        patched.append(r)
    raws = patched

    has_any_percent = any(r.has_percent for r in raws)
    not_available_count = sum(1 for r in raws if (not r.has_percent and r.is_not_available))
    is_wrong_tab = (not has_any_percent) and (not_available_count == 0)

    ctx.footer_decisions = {}
    for r in raws:
        if r.has_percent:
            gate = FooterGate.OK
        else:
            if r.is_not_available:
                gate = FooterGate.NOT_AVAILABLE
            else:
                gate = FooterGate.WRONG_TAB if is_wrong_tab else FooterGate.UNKNOWN

        ctx.footer_decisions[r.emiten] = FooterDecision(gate=gate, raw_text=r.raw_text)

    ctx.screen_mode = "wrong_tab" if is_wrong_tab else "time_ok"

    ok_count = sum(1 for d in ctx.footer_decisions.values() if d.gate == FooterGate.OK)
    na_count = sum(1 for d in ctx.footer_decisions.values() if d.gate == FooterGate.NOT_AVAILABLE)
    wt_count = sum(1 for d in ctx.footer_decisions.values() if d.gate == FooterGate.WRONG_TAB)
    unk_count = sum(1 for d in ctx.footer_decisions.values() if d.gate == FooterGate.UNKNOWN)

    print(
        f"[D_footer_cek] screen_mode={ctx.screen_mode} "
        f"OK={ok_count} NOT_AVAILABLE={na_count} WRONG_TAB={wt_count} UNKNOWN={unk_count}"
    )

    # (opsional) print detail emiten bermasalah
    if na_count:
        print("[D_footer_cek] Emiten NOT_AVAILABLE:")
        for em, d in ctx.footer_decisions.items():
            if d.gate == FooterGate.NOT_AVAILABLE:
                print(f"  - {em} | text='{d.raw_text}'")

    if wt_count:
        print("[D_footer_cek] Indikasi SALAH TAB (Chart/Price).")

    if unk_count and not is_wrong_tab:
        print("[D_footer_cek] Emiten UNKNOWN:")
        for em, d in ctx.footer_decisions.items():
            if d.gate == FooterGate.UNKNOWN:
                print(f"  - {em} | text='{d.raw_text}'")

    return ctx
