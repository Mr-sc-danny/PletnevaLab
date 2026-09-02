# nmr_autophase_baseline.py

## Purpose

Automatically phase-correct and baseline-correct a 1D NMR spectrum exported
from TopSpin as ASCII text, with the correction deliberately focused on a
negative-ppm region and an extra emphasis window around a chosen chemical
shift (default: -3 ppm).

This exists because manual phasing in TopSpin (`.ph`, dragging PH0/PH1
sliders against reference peaks) is fine for one spectrum but doesn't scale,
and because a single global phase/baseline choice can't be "best" for every
region of a wide, complex spectrum at once — this script lets you say
explicitly which region matters most and optimizes for that.

No third-party packages beyond numpy / scipy / pandas / matplotlib are used
(no install permissions were available in the environment this was written
in, so nothing beyond the standard scientific-Python stack is required).

Note: at the time this was written, the `PletnevaLabForBots` reference repo
had no existing script for NMR phase or baseline correction, so everything
below was written from scratch rather than adapted from an existing tool.

## Usage

Command line:

```bash
python nmr_autophase_baseline.py input.txt --outdir ./out
```

Optional flags (all have defaults, shown below):

| Flag | Default | Meaning |
|---|---|---|
| `--outdir` | `./nmr_out` | where the CSV and PNGs are written |
| `--focus-max` | `0.0` | ppm boundary of the region to optimize (everything with ppm < this value is "in scope") |
| `--emphasis-center` | `-3.0` | ppm center of the extra-weighted window |
| `--emphasis-width` | `0.3` | half-width (ppm) of the emphasis window |
| `--emphasis-gain` | `4.0` | how much extra negativity penalty inside the emphasis window, relative to the rest of the focus region |
| `--als-lam` | `5e4` | baseline smoothness (bigger = smoother, less peak-sensitive) |
| `--als-p` | `1e-3` | baseline asymmetry (smaller = baseline sits closer to peak valleys, but more biased low before recentering) |

Or import it directly and call the driver function:

```python
from nmr_autophase_baseline import process_spectrum

result = process_spectrum(
    "input.txt", outdir="./out",
    focus_max=0.0, emphasis_center=-3.0,
)
print(result["phc0"], result["phc1"])
```

## Input

A TopSpin ASCII export with this header format:

```
# LEFT = 15.750659942626953 ppm. RIGHT = -6.187546989646183 ppm.
# SIZE = 32768 ( = number of points)
```

followed by one value per line, either:
- **real-only**: `151625.25`
- **complex**: `151625.25-77930.125i` (scientific notation like
  `-813326.0+1.0133695375E7i` is also handled)

The parser auto-detects which format it's looking at from the first data
line, so you don't need to tell it.

## Calculation

**1. Parsing** (`load_topspin_ascii`) — reads the LEFT/RIGHT/SIZE header to
build a ppm axis, and reads each data line into a complex NumPy array
(imaginary part is 0 if the file was real-only).

**2. Phase correction** (`autophase` / `apply_phase` / `_autophase_cost`) —

- A single global zero-order (PH0) + first-order (PH1) phase is applied to
  the *whole* spectrum — phase is a property of the whole spectrum, not
  just the region you care about, even though we only *score* the focus
  region.
- The phase is chosen by minimizing a cost function evaluated only on
  `ppm < focus_max`:
  - **Entropy of the first derivative** (the "ACME" approach): a
    well-phased spectrum concentrates its derivative into a few sharp
    jumps; a badly-phased one smears it everywhere. Lower entropy = more
    concentrated = better phased.
  - **Negativity penalty**: squared sum of any negative-going signal,
    since real absorptive peaks shouldn't dip below baseline.
  - **Extra-weighted negativity penalty** inside a window around
    `emphasis_center` (default -3 ppm), multiplied by `emphasis_gain`, so
    that specific region is prioritized even at a small cost to the rest
    of the focus region.
- The cost is minimized with Nelder-Mead from a 13×9 grid of starting
  points (multi-start), since the cost surface can have local minima that
  a single optimizer run could get stuck in.

**3. Baseline correction** (`baseline_als` / `detect_peak_mask` /
`baseline_correct`) —

- Asymmetric Least Squares (ALS) fits a smooth curve that's penalized for
  roughness (via a discrete second-derivative matrix, scaled by `als-lam`)
  and re-weighted each iteration so points above the current fit (likely
  peaks) barely pull it up, while points below pull it down — the fit
  converges to track the valleys between peaks.
- This asymmetry causes the fitted baseline to sit systematically *below*
  the true noise floor. Peak regions are auto-detected in the residual
  (`scipy.signal.find_peaks` + `peak_widths`), the median of the
  *peak-free* residual is computed, and that constant is added back to
  the baseline so quiet regions genuinely center on zero rather than
  landing a few thousand units above it.

**4. Output assembly** (`process_spectrum`) — runs the above in order and
writes the CSV + plots described below.

## Output

For an input file `foo.txt`, running the script writes three files to
`--outdir`:

- **`foo_phased_baseline_corrected.csv`** — one row per point in the focus
  region, columns: `ppm`, `real_raw`, `imag_raw`, `real_phased`,
  `imag_phased`, `baseline_fit`, `real_phased_baseline_corrected`.
- **`foo_full_spectrum_before_after.png`** — two stacked panels showing the
  real part of the *entire* spectrum (not just the focus region) before and
  after phasing, so you can see whether the chosen phase also affected
  regions outside the focus region.
- **`foo_focus_region_corrected.png`** — the final phased + baseline
  corrected trace for the focus region only, with a dotted line marking
  the emphasis center.

It also prints the chosen `PH0`, `PH1`, and final cost value to stdout,
and (if imported rather than run from the CLI) returns a dict with those
values plus the file paths and the corrected arrays.

## Known limitation

This only fits a *global* two-parameter (PH0, PH1) phase — the same kind of
correction available in TopSpin's interactive phasing tool. If a spectrum
has genuinely non-linear phase error across its full width (common in wide
sweep-width paramagnetic NMR), no choice of PH0/PH1 will look good
everywhere at once; the script will do its best specifically for the focus
region (and especially the emphasis window) at the cost of leaving other
regions exactly as dispersive as they started. There is no automatic
detection of this trade-off — check the "before/after, full spectrum" PNG
to see whether it happened on your data.
