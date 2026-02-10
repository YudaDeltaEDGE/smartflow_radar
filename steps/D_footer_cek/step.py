# steps/D_footer_cek/step.py
from __future__ import annotations

from pipeline.types import Context, FooterGate, FooterDecision
from .config import FooterCekConfig
from .service import FooterCekService


def jalankan_step_D_footer_cek(ctx: Context) -> Context:
    """
    STEP D - FOOTER CEK (GATE)

    Input:
      - ctx.footer_cek_items (hasil crop dari Step B_roi)

    Output:
      - ctx.footer_decisions: dict emiten -> FooterDecision(gate, raw_text)
      - ctx.screen_mode: "wrong_tab" atau "time_ok"

    Rule:
      - Jika ada '%' -> OK (boleh lanjut E/F)
      - Jika tidak ada '%':
          - Jika terdeteksi 'not available' -> NOT_AVAILABLE (eligible untuk retry capture nanti)
          - Jika indikasi global wrong tab -> WRONG_TAB (fail-fast nanti)
          - Selain itu -> UNKNOWN
    """

    cfg = FooterCekConfig()
    svc = FooterCekService(bin_threshold=cfg.bin_threshold)

    raws = svc.run(ctx.footer_cek_items)

    # Deteksi global "WRONG_TAB":
    # - Tidak ada '%' sama sekali di semua tile
    # - Dan tidak ada indikasi "not available"
    has_any_percent = any(r.has_percent for r in raws)
    not_available_count = sum(1 for r in raws if (not r.has_percent and r.is_not_available))

    is_wrong_tab = (not has_any_percent) and (not_available_count == 0)

    # Isi keputusan per emiten
    ctx.footer_decisions = {}
    for r in raws:
        if r.has_percent:
            gate = FooterGate.OK
        else:
            if r.is_not_available:
                gate = FooterGate.NOT_AVAILABLE
            else:
                gate = FooterGate.WRONG_TAB if is_wrong_tab else FooterGate.UNKNOWN

        ctx.footer_decisions[r.emiten] = FooterDecision(
            gate=gate,
            raw_text=r.raw_text,
        )

    ctx.screen_mode = "wrong_tab" if is_wrong_tab else "time_ok"

    # Log ringkas agar gampang debugging
    ok_count = sum(1 for d in ctx.footer_decisions.values() if d.gate == FooterGate.OK)
    na_count = sum(1 for d in ctx.footer_decisions.values() if d.gate == FooterGate.NOT_AVAILABLE)
    wt_count = sum(1 for d in ctx.footer_decisions.values() if d.gate == FooterGate.WRONG_TAB)
    unk_count = sum(1 for d in ctx.footer_decisions.values() if d.gate == FooterGate.UNKNOWN)

    print(
        f"[D_footer_cek] screen_mode={ctx.screen_mode} "
        f"OK={ok_count} NOT_AVAILABLE={na_count} WRONG_TAB={wt_count} UNKNOWN={unk_count}"
    )

    # Print daftar emiten yang false-ish untuk kamu cek cepat
    if na_count:
        print("[D_footer_cek] Emiten NOT_AVAILABLE (eligible retry capture nanti):")
        for em, d in ctx.footer_decisions.items():
            if d.gate == FooterGate.NOT_AVAILABLE:
                print(f"  - {em} | text='{d.raw_text}'")

    if wt_count:
        print("[D_footer_cek] Indikasi SALAH TAB (Chart/Price). Pipeline harus fail-fast nanti.")

    if unk_count and not is_wrong_tab:
        print("[D_footer_cek] Emiten UNKNOWN (OCR noise / kasus lain):")
        for em, d in ctx.footer_decisions.items():
            if d.gate == FooterGate.UNKNOWN:
                print(f"  - {em} | text='{d.raw_text}'")

    return ctx
