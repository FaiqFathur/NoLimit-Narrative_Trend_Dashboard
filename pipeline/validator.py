import re
from dataclasses import dataclass, field

HARD_BLOCK_PATTERN = re.compile(
    r"\b("
    r"open bo|bokep|porno|pornhub|xnxx|xvideos|"
    r"jual konten|jual video|video syur|onlyfans|"
    r"bkep|lendir|sange|ngewe|bokp|vcs|bugil|"
    r"telanjang|colmek|crot|desah|jablay|lonte|"
    r"michat|scandal|slutty|doodstream|videy|dood|"
    r"cdnvidey|tobrut|toge|pemersatu bangsa|link pemersatu|jav|j4v|simontok|fap"
    r")\b",
    re.IGNORECASE,
)

SUSPICIOUS_TERMS = {
    "viral", "cdn", "jp", "gacha", "terabox", "uc-share", "hijab viral",
    "slot", "judi", "judol", "togel", "zeus", "pragmatic", "fafafa", "olympus", 
    "mahjong ways", "sbobet", "parlay"
}

PROMO_SIGNALS = {
    "gacor", "maxwin", "depo", "bonus", "scatter", "dana kaget", "saldo dana",
    "daftar", "rtp", "link", "cuan", "aplikasi penghasil uang",
    "withdraw", "telegram", "whatsapp"
}

NEWS_SIGNALS = {
    "polisi", "kasus", "tersangka",
    "ditangkap", "pemerintah", "regulasi",
    "larangan", "penyelidikan", "game"
}

@dataclass
class ModerationResult:
    status: str
    score: int
    reasons: list[str] = field(default_factory=list)

def moderate_content(text: str) -> ModerationResult:
    if not text or not text.strip():
        return ModerationResult("blocked", 10, ["empty_content"])

    normalized = text.lower()

    if HARD_BLOCK_PATTERN.search(normalized):
        return ModerationResult(
            "blocked",
            10,
            ["explicit_nsfw"],
        )

    found_suspicious = {
        word for word in SUSPICIOUS_TERMS
        if re.search(rf"\b{re.escape(word)}\b", normalized)
    }

    found_promo = {
        word for word in PROMO_SIGNALS
        if re.search(rf"\b{re.escape(word)}\b", normalized)
    }

    found_news = {
        word for word in NEWS_SIGNALS
        if re.search(rf"\b{re.escape(word)}\b", normalized)
    }

    score = len(found_suspicious)
    score += len(found_promo) * 2

    # Safe context hanya mengurangi risiko kata ambigu.
    if found_news and not found_promo:
        score = max(0, score - 2)

    reasons = sorted(found_suspicious | found_promo)

    if score >= 4:
        status = "blocked"
    elif score >= 2:
        status = "flagged"
    else:
        status = "allowed"

    return ModerationResult(status, score, reasons)

if __name__ == "__main__":
    print(moderate_content("Berita ini viral di media sosial"))
    # allowed
    
    print(moderate_content("Link video viral terbaru klik sekarang"))
    # flagged
    
    print(moderate_content("Slot gacor JP maxwin, daftar dan depo sekarang"))
    # blocked
    
    print(moderate_content("Polisi menangkap tersangka judi online"))
    # allowed atau flagged, sesuai threshold
    
    print(moderate_content("Bocoran rtp fafafa hari ini, auto cuan bosku"))
    # blocked
