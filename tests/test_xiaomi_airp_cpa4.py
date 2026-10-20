from homeassistant.helpers.entity import EntityCategory

from custom_components.xiaomi_miot.sensor import SensorEntity


MODEL = "xiaomi.airp.cpa4"


def find_prop_converter(device, domain, prop_name):
    return next(
        (
            converter
            for converter in device.converters
            if converter.domain == domain
            and getattr(converter, "prop", None)
            and converter.prop.name == prop_name
        ),
        None,
    )


def test_xiaomi_airp_cpa4_exposes_supported_entities(make_device, load_miot_spec):
    device = make_device(load_miot_spec(f"{MODEL}.json"), model=MODEL)
    converters = {converter.full_name for converter in device.converters}

    assert {
        "fan.air_purifier.on",
        "switch.alarm",
        "switch.physical_controls_locked",
        "select.screen.brightness",
        "select.aqi.aqi_updata_heartbeat",
        "number.custom_service.favorite_level",
        "button.filter.reset_filter_life",
    } <= converters
    for prop_name in [
        "pm2_5_density",
        "filter_life_level",
        "filter_left_time",
        "filter_used_time",
        "fault",
        "motor_speed_rpm",
    ]:
        assert find_prop_converter(device, "sensor", prop_name), prop_name


def test_xiaomi_airp_cpa4_sensor_categories_and_units(make_device, load_miot_spec):
    device = make_device(load_miot_spec(f"{MODEL}.json"), model=MODEL)

    pm25 = SensorEntity(device, find_prop_converter(device, "sensor", "pm2_5_density"))
    fault = SensorEntity(device, find_prop_converter(device, "sensor", "fault"))
    motor_rpm = SensorEntity(device, find_prop_converter(device, "sensor", "motor_speed_rpm"))

    assert pm25.entity_category is None
    assert fault.entity_category is EntityCategory.DIAGNOSTIC
    assert motor_rpm.entity_category is EntityCategory.DIAGNOSTIC
    assert motor_rpm.native_unit_of_measurement == "rpm"


def test_xiaomi_airp_cpa4_omits_factory_properties(make_device, load_miot_spec):
    device = make_device(load_miot_spec(f"{MODEL}.json"), model=MODEL)
    mapping = device.miot_mapping()

    assert not any("filter_used_time_dbg" in key for key in mapping)
    assert not any("country_code" in key for key in mapping)
