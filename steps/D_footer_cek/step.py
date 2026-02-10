# steps/D_footer_cek/step.py
from __future__ import annotations

from pipeline.types import Context
from .config import FooterCekConfig
from .service import FooterCekService


def jalankan_step_D_footer_cek(ctx: Context) -> Context:
    """
    STEP D - FOOTER CEK (GATE)
    Input: ctx.footer_cek_items
    Output: (sementara) print ringkasan:
      - emiten yang tidak ada '%'
      - emiten yang terindikasi 'is not available'
    """
    cfg = FooterCekConfig()
    svc = FooterCekService(bin_threshold=cfg.bin_threshold)

    results = svc.run(ctx.footer_cek_items)

    tanpa_persen = [r for r in results if not r.has_percent]
    not_available = [r for r in results if (not r.has_percent and r.is_not_available)]

    print(f"[D_footer_cek] Total items: {len(results)}")
    print(f"[D_footer_cek] Tanpa %: {len(tanpa_persen)}")
    if tanpa_persen:
        print("[D_footer_cek] Emiten tanpa % (perlu cek tile / kemungkinan not available):")
        for r in tanpa_persen:
            print(f"  - {r.emiten} | text='{r.raw_text}'")

    print(f"[D_footer_cek] Terindikasi NOT AVAILABLE: {len(not_available)}")
    if not_available:
        print("[D_footer_cek] Emiten NOT AVAILABLE (aman: skip buy/sell lot):")
        for r in not_available:
            print(f"  - {r.emiten} | text='{r.raw_text}'")

    return ctx
