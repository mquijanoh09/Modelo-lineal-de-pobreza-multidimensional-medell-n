# -*- coding: utf-8 -*-
"""Verifica contra los CSV las cifras del 12-nov que el paper toma de cifras.tex (macros \\z...).
Uso: python3 m34_verificar_12nov.py <paper/cifras.tex>"""
import re
import sys

import pandas as pd

R = "resultados/m34/"


def main(cifras):
    mac = dict(re.findall(r"\\newcommand\{\\(z\w+|cIPglobalDiez)\}\{([^}]*)\}", open(cifras, encoding="utf-8").read()))
    num = lambda k: float(mac[k].replace("\\,\\%", "").replace(".", "").replace(",", ".").split()[0])
    c = pd.read_csv(R + "costo_meta_zona_crudo_12nov.csv"); t = pd.read_csv(R + "ic_costo_meta_zona_12nov.csv")
    q = pd.read_csv(R + "ic_rmax_12nov.csv"); cob = pd.read_csv(R + "cobertura_rB_crudo_12nov.csv")
    rm = pd.read_csv(R + "rmax_12nov.csv")
    ok = []
    chk = lambda n, cond: ok.append((n, bool(cond)))
    chk("zReplicas", c.replica.nunique() == num("zReplicas"))
    chk("zCorridas", (c.estado == "Optimal").sum() == len(c) == num("zCorridas"))
    chk("zGapMax", c.gap.max() < 8.8e-7 + 5e-9)
    b = t.meta <= 0.10 + 1e-9; a = t.meta >= 0.20 - 1e-9
    chk("zMtresIPmin/max", round(t.m3_sobre_IP.min(), 1) == num("zMtresIPmin") and round(t.m3_sobre_IP.max(), 1) == num("zMtresIPmax"))
    chk("zMtresIPbaja", mac["zMtresIPbaja"] == f"{t.m3_sobre_IP[b].min():.1f} a {t.m3_sobre_IP[b].max():.1f}".replace(".", ","))
    chk("zMtresIPalta", mac["zMtresIPalta"] == f"{t.m3_sobre_IP[a].min():.1f} a {t.m3_sobre_IP[a].max():.1f}".replace(".", ","))
    chk("zMcuatroIP", round(t.m4_sobre_IP.min(), 1) == num("zMcuatroIPmin") and round(t.m4_sobre_IP.max(), 1) == num("zMcuatroIPmax"))
    chk("zMcuatroMtres", ((t.M4_sobre_M3_ic_sup < 1).sum(), (t.M4_sobre_M3_ic_inf > 1).sum(),
                          ((t.M4_sobre_M3_ic_inf <= 1) & (t.M4_sobre_M3_ic_sup >= 1)).sum())
        == (num("zMcuatroMtresMenor"), num("zMcuatroMtresMayor"), num("zMcuatroMtresIgual")))
    d6 = t[t.meta >= 0.06 - 1e-9]
    chk("zPlac", (d6.M4_sobre_placebo_ic_sup < 1).all() and round(100 * (1 - d6.M4_sobre_placebo.max())) == num("zPlacMin")
        and round(100 * (1 - d6.M4_sobre_placebo.min())) == num("zPlacMax"))
    chk("zIncl", mac["zInclMtres"].startswith(f"{round(100*t.m3_inclusion.min())} y {round(100*t.m3_inclusion.max())}")
        and mac["zInclMcuatro"].startswith(f"{round(100*t.m4_inclusion.min())} y {round(100*t.m4_inclusion.max())}"))
    chk("zExclMtres", mac["zExclMtres"].startswith(f"{round(100*t.m3_exclusion.min())} y {round(100*t.m3_exclusion.max())}"))
    chk("zIPzonaDiez", round(t.set_index(t.meta.round(2)).IP[0.10], 2) == num("zIPzonaDiez"))
    chk("zCorridasCob", (cob.estado.str.startswith("Infeasible")).sum() == num("zCorridasCob")
        and not (cob.estado == "Optimal").any())
    chk("zCorridasRmax", len(rm) == num("zCorridasRmax") and rm.r_max.notna().all())
    chk("rmax <= IP y mejor M3 < r_B", (q.m3_mejor < q.r_B).all() and (q.IP_max >= q.r_B).all())
    chk("zRmaxFrac", round(100 * (q.m3 / q.IP_max).iloc[-1]) == num("zRmaxFracMax") and (q.m3 / q.IP_max).iloc[0] == 0)
    for n, v in ok:
        print("OK " if v else "FALLA", n)
    print(f"{sum(v for _, v in ok)}/{len(ok)}")


if __name__ == "__main__":
    main(sys.argv[1])
