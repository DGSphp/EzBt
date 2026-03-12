from unittest.mock import MagicMock
from coordinator import BluetoothCoordinator

def test_device_filtering():
    hass = MagicMock()
    coordinator = BluetoothCoordinator(hass)
    
    # Mock service info for a relevant device
    relevant_service_info = MagicMock()
    relevant_service_info.device.name = "Sony XM4 Speaker"
    relevant_service_info.device.address = "00:1A:7D:F0:11:22"
    relevant_service_info.advertisement.local_name = "Sony XM4 Speaker"
    relevant_service_info.rssi = -50
    
    coordinator._async_device_discovered(relevant_service_info, "discovered")
    assert "00:1A:7D:F0:11:22" in coordinator.discovered_devices
    
    # Mock service info for an irrelevant device
    irrelevant_service_info = MagicMock()
    irrelevant_service_info.device.name = "Unknown Device"
    irrelevant_service_info.device.address = "11:22:33:44:55:66"
    irrelevant_service_info.advertisement.local_name = None
    
    coordinator._async_device_discovered(irrelevant_service_info, "discovered")
    assert "11:22:33:44:55:66" not in coordinator.discovered_devices

    # Mock service info for a HID device
    hid_service_info = MagicMock()
    hid_service_info.device.name = "Magic Mouse"
    hid_service_info.device.address = "AA:BB:CC:DD:EE:FF"
    hid_service_info.advertisement.local_name = "Magic Mouse"
    hid_service_info.rssi = -60
    
    coordinator._async_device_discovered(hid_service_info, "discovered")
    assert "AA:BB:CC:DD:EE:FF" in coordinator.discovered_devices

    # Mock service info for the specific Bluetooth Radio device
    radio_service_info = MagicMock()
    radio_service_info.device.name = "Bluetooth Radio (0bda:a729)"
    radio_service_info.device.address = "00:E0:12:34:56:8D"
    radio_service_info.advertisement.local_name = "Bluetooth Radio"
    radio_service_info.rssi = -45
    
    coordinator._async_device_discovered(radio_service_info, "discovered")
    assert "00:E0:12:34:56:8D" in coordinator.discovered_devices

    # Mock service info for an Audio device
    audio_service_info = MagicMock()
    audio_service_info.device.name = "My Audio System"
    audio_service_info.device.address = "11:22:33:44:55:66"
    audio_service_info.advertisement.local_name = "My Audio System"
    audio_service_info.rssi = -55
    
    coordinator._async_device_discovered(audio_service_info, "discovered")
    assert "11:22:33:44:55:66" in coordinator.discovered_devices
