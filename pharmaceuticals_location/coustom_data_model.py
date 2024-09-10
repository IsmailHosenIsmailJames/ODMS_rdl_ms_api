from dataclasses import dataclass
from typing import Optional, Any, TypeVar, Type, cast


T = TypeVar("T")


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def is_type(t: Type[T], x: Any) -> T:
    assert isinstance(x, t)
    return x


def to_float(x: Any) -> float:
    assert isinstance(x, (int, float))
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class SavePharmaceuticalsLocationData:
    id: None
    route_code: Optional[int] = None
    route_name: Optional[str] = None
    da_code: Optional[int] = None
    da_name: Optional[str] = None
    partner: Optional[int] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_mobile: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SavePharmaceuticalsLocationData':
        assert isinstance(obj, dict)
        id = from_none(obj.get("id"))
        route_code = from_union([from_none, lambda x: int(from_str(x))], obj.get("route_code"))
        route_name = from_union([from_str, from_none], obj.get("route_name"))
        da_code = from_union([from_int, from_none], obj.get("da_code"))
        da_name = from_union([from_str, from_none], obj.get("da_name"))
        partner = from_union([from_none, lambda x: int(from_str(x))], obj.get("partner"))
        customer_name = from_union([from_str, from_none], obj.get("customer_name"))
        customer_address = from_union([from_str, from_none], obj.get("customer_address"))
        customer_mobile = from_union([from_str, from_none], obj.get("customer_mobile"))
        latitude = from_union([from_float, from_none], obj.get("latitude"))
        longitude = from_union([from_float, from_none], obj.get("longitude"))
        return SavePharmaceuticalsLocationData(id, route_code, route_name, da_code, da_name, partner, customer_name, customer_address, customer_mobile, latitude, longitude)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.id is not None:
            result["id"] = from_none(self.id)
        if self.route_code is not None:
            result["route_code"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.route_code)
        if self.route_name is not None:
            result["route_name"] = from_union([from_str, from_none], self.route_name)
        if self.da_code is not None:
            result["da_code"] = from_union([from_int, from_none], self.da_code)
        if self.da_name is not None:
            result["da_name"] = from_union([from_str, from_none], self.da_name)
        if self.partner is not None:
            result["partner"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.partner)
        if self.customer_name is not None:
            result["customer_name"] = from_union([from_str, from_none], self.customer_name)
        if self.customer_address is not None:
            result["customer_address"] = from_union([from_str, from_none], self.customer_address)
        if self.customer_mobile is not None:
            result["customer_mobile"] = from_union([from_str, from_none], self.customer_mobile)
        if self.latitude is not None:
            result["latitude"] = from_union([to_float, from_none], self.latitude)
        if self.longitude is not None:
            result["longitude"] = from_union([to_float, from_none], self.longitude)
        return result


def save_pharmaceuticals_location_data_from_dict(s: Any) -> SavePharmaceuticalsLocationData:
    return SavePharmaceuticalsLocationData.from_dict(s)


def save_pharmaceuticals_location_data_to_dict(x: SavePharmaceuticalsLocationData) -> Any:
    return to_class(SavePharmaceuticalsLocationData, x)
