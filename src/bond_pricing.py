from __future__ import annotations

from dataclasses import dataclass
import calendar
from datetime import date, datetime


SUPPORTED_DAY_COUNTS = {"Actual/Actual", "30/360"}


@dataclass(frozen=True)
class BondInput:
    face_value: float
    clean_price_per_100: float
    annual_coupon_rate: float
    coupon_frequency: int
    last_coupon_date: date
    settlement_date: date
    next_coupon_date: date
    day_count_convention: str


@dataclass(frozen=True)
class BondPriceResult:
    dollar_clean_price: float
    coupon_per_period: float
    accrued_fraction: float
    accrued_interest: float
    dirty_price: float

    def rounded(self, digits: int = 6) -> dict[str, float]:
        return {
            "dollar_clean_price": round(self.dollar_clean_price, digits),
            "coupon_per_period": round(self.coupon_per_period, digits),
            "accrued_fraction": round(self.accrued_fraction, digits),
            "accrued_interest": round(self.accrued_interest, digits),
            "dirty_price": round(self.dirty_price, digits),
        }


def parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def bond_input_from_dict(raw: dict) -> BondInput:
    return BondInput(
        face_value=float(raw["face_value"]),
        clean_price_per_100=float(raw["clean_price_per_100"]),
        annual_coupon_rate=float(raw["annual_coupon_rate"]),
        coupon_frequency=int(raw["coupon_frequency"]),
        last_coupon_date=parse_date(raw["last_coupon_date"]),
        settlement_date=parse_date(raw["settlement_date"]),
        next_coupon_date=parse_date(raw["next_coupon_date"]),
        day_count_convention=raw["day_count_convention"],
    )


def actual_actual_days(start: date, end: date) -> int:
    return (end - start).days


def is_last_day_of_february(value: date) -> bool:
    return value.month == 2 and value.day == calendar.monthrange(value.year, 2)[1]


def thirty_360_us_days(start: date, end: date) -> int:
    start_day = 30 if is_last_day_of_february(start) else min(start.day, 30)
    end_day = end.day

    if is_last_day_of_february(start) and is_last_day_of_february(end):
        end_day = 30
    elif start_day >= 30 and end.day == 31:
        end_day = 30

    return (
        360 * (end.year - start.year)
        + 30 * (end.month - start.month)
        + (end_day - start_day)
    )


def day_count_days(start: date, end: date, convention: str) -> int:
    if convention == "Actual/Actual":
        return actual_actual_days(start, end)
    if convention == "30/360":
        return thirty_360_us_days(start, end)
    raise ValueError(f"Unsupported day-count convention: {convention}")


def accrued_fraction(
    last_coupon_date: date,
    settlement_date: date,
    next_coupon_date: date,
    day_count_convention: str,
) -> float:
    if day_count_convention not in SUPPORTED_DAY_COUNTS:
        raise ValueError(f"Unsupported day-count convention: {day_count_convention}")
    if not last_coupon_date <= settlement_date <= next_coupon_date:
        raise ValueError("Settlement date must be within the coupon period.")

    elapsed_days = day_count_days(last_coupon_date, settlement_date, day_count_convention)
    period_days = day_count_days(last_coupon_date, next_coupon_date, day_count_convention)
    if period_days <= 0:
        raise ValueError("Coupon period must have positive length.")

    return elapsed_days / period_days


def price_bond(bond: BondInput) -> BondPriceResult:
    if bond.face_value <= 0:
        raise ValueError("Face value must be positive.")
    if bond.coupon_frequency <= 0:
        raise ValueError("Coupon frequency must be positive.")

    dollar_clean_price = bond.face_value * bond.clean_price_per_100 / 100
    coupon_per_period = bond.face_value * bond.annual_coupon_rate / bond.coupon_frequency
    fraction = accrued_fraction(
        bond.last_coupon_date,
        bond.settlement_date,
        bond.next_coupon_date,
        bond.day_count_convention,
    )
    accrued_interest = coupon_per_period * fraction
    dirty_price = dollar_clean_price + accrued_interest

    return BondPriceResult(
        dollar_clean_price=dollar_clean_price,
        coupon_per_period=coupon_per_period,
        accrued_fraction=fraction,
        accrued_interest=accrued_interest,
        dirty_price=dirty_price,
    )
