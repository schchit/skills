# Return Estimation — Ước tính Khả năng Sinh lời

> Phương pháp định lượng để estimate lợi nhuận kỳ vọng theo thời gian,
> kết hợp dữ liệu lịch sử và phân tích kịch bản.

---

## Phương pháp 1: Historical Return Analysis

### API: VNDirect dChart

Fetch lịch sử giá hàng ngày (daily OHLCV):

```
GET https://dchart-api.vndirect.com.vn/dchart/history
    ?symbol=FPT
    &resolution=D
    &from=1609459200   (Unix timestamp — 2021-01-01)
    &to=1742400000     (Unix timestamp — today)
```

**Không cần authentication.** Response format:
```json
{
  "t": [1609459200, ...],   // timestamps
  "c": [72500, ...],        // close prices (VND)
  "o": [...], "h": [...], "l": [...], "v": [...]
}
```

### Metrics cần tính

| Metric | Công thức | Ý nghĩa |
|--------|-----------|---------|
| **Return N tháng** | `(close_now / close_Nmonths_ago - 1) × 100` | Lợi nhuận thực tế |
| **CAGR** | `(close_now / close_Nyears_ago)^(1/N) - 1` | Tăng trưởng kép/năm |
| **Volatility** | `std(daily_returns) × √252` | Rủi ro hàng năm |
| **Max Drawdown** | `min((price - running_max) / running_max)` | Mức giảm tối đa từ đỉnh |
| **Sharpe Ratio** | `(CAGR - rf_rate) / volatility` | Return/risk (rf = 4.5%) |

### Benchmark tham chiếu
- **Gửi ngân hàng**: 5.5%/năm (kỳ hạn 12 tháng)
- **VN-Index trung bình**: ~10–12%/năm (2010–2024)
- **Inflation VN**: ~3–4%/năm

---

## Phương pháp 2: Scenario Analysis (3 kịch bản)

Dựa trên volatility lịch sử × time horizon:

```
Bear (bi quan):    Return = risk-free rate (5.5%) ± 0 (giữ nguyên giá, chỉ dividend)
Base (trung bình): Return = EPS growth rate (consensus) + P/E stable
Bull (lạc quan):   Return = EPS growth + P/E re-rating + catalyst premium
```

### Công thức ước tính

```python
bear_annual  = max(rf_rate, cagr_3y - 1.0 * volatility)   # 1 std dev dưới mean
base_annual  = cagr_3y                                      # mean reversion
bull_annual  = cagr_3y + 0.5 * volatility                  # 0.5 std dev trên mean

def project(principal, annual_rate, years):
    return principal * (1 + annual_rate) ** years
```

### Template Output

```
## 📈 Estimate Lợi Nhuận — [TICKER]
Vốn đầu tư: X triệu VND | Giá hiện tại: X,XXX VND

### Lịch sử (thực tế)
Giá 1 năm trước:  X,XXX | Return: +/-XX.X%
Giá 3 năm trước:  X,XXX | CAGR: +/-XX.X%/năm
Giá 5 năm trước:  X,XXX | CAGR: +/-XX.X%/năm
Volatility/năm:   XX.X%
Max Drawdown:     -XX.X%
Sharpe Ratio:     X.XX

### Dự báo theo kịch bản (từ giá hiện tại)
                    6 tháng    1 năm     3 năm     5 năm
Bear  (bi quan):    +X.X%     +XX.X%    +XX.X%    +XX.X%  → VND X.X triệu
Base  (trung bình): +XX.X%    +XX.X%    +XX.X%    +XX.X%  → VND X.X triệu
Bull  (lạc quan):   +XX.X%    +XX.X%    +XX.X%    +XX.X%  → VND X.X triệu

### So sánh với tài sản khác (vốn X triệu, 3 năm)
Gửi ngân hàng 5.5%/năm:        +X.X triệu  (tổng: X.X triệu)
[TICKER] Base case:             +X.X triệu  (tổng: X.X triệu)
VN-Index trung bình 11%/năm:    +X.X triệu  (tổng: X.X triệu)

### Catalyst & Timeline (sự kiện tác động giá)
- [Catalyst 1]: dự kiến tháng X/20XX → +XX% nếu xảy ra
- Nâng hạng thị trường FTSE/MSCI: dự kiến 2026–2027 → inflow ~$X tỷ
- Kết quả kinh doanh Q1: tháng 4/20XX
```

---

## Phương pháp 3: Script tự động `estimate_returns.py`

Xem `scripts/estimate_returns.py` để tính tự động với Python.

Script thực hiện:
1. Fetch 5 năm daily data từ VNDirect dChart API
2. Tính CAGR, volatility, max drawdown, Sharpe Ratio
3. Build 3 scenario projections (Bear/Base/Bull)
4. So sánh với benchmark (ngân hàng, VN-Index)
5. Output bảng đầy đủ

**Sử dụng:**
```bash
python3 scripts/estimate_returns.py FPT
python3 scripts/estimate_returns.py VCB --capital 100  # 100 triệu VND
python3 scripts/estimate_returns.py HPG --capital 50 --years 3
```

---

## Lưu ý quan trọng

### Giới hạn của mô hình
- **Past performance ≠ future results** — đặc biệt với cổ phiếu chu kỳ (thép, BĐS)
- Scenario analysis dựa trên **volatility lịch sử** — volatility tương lai có thể khác
- Không tính **dividend reinvestment** (thêm ~2–5%/năm cho cổ phiếu dividend cao)
- Không tính **thuế** (thuế TNCN 0.1% trên doanh số bán, hiện hành)

### Khi nào dùng phương pháp nào
| Tình huống | Phương pháp |
|-----------|-------------|
| Stock đã có 3+ năm lịch sử | Historical Return + Scenario |
| Stock mới IPO (<2 năm) | Chỉ dùng Sector CAGR benchmark |
| Cổ phiếu chu kỳ (thép, BĐS) | Nhấn mạnh Max Drawdown, dùng Bear case |
| Blue chip ổn định (VNM, GAS) | Base case đáng tin, Sharpe ratio quan trọng |

### Benchmark lãi suất ngân hàng (cập nhật Q1 2026)
| Kỳ hạn | Lãi suất |
|--------|---------|
| 6 tháng | 4.8–5.2% |
| 12 tháng | 5.3–5.8% |
| 24 tháng | 5.5–6.0% |
| **Dùng 5.5%/năm làm baseline** | |

---

*Disclaimer: Ước tính lợi nhuận chỉ mang tính tham khảo. Không phải khuyến nghị đầu tư.*
