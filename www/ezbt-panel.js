import { LitElement, html, css } from "https://unpkg.com/lit@2.6.1/index.js?module";

class EzBtPanel extends LitElement {
    static properties = {
        hass: { type: Object },
        devices: { type: Array },
        isScanning: { type: Boolean },
    };

    constructor() {
        super();
        this.devices = [];
        this.isScanning = false;
    }

    firstUpdated() {
        this.scanDevices();
    }

    static styles = css`
    :host {
      display: block;
      padding: 16px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }
    .scan-button {
      background: #007aff;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 12px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
      transition: background 0.2s, box-shadow 0.2s;
    }
    .scan-button:active {
      background: #0056b3;
    }
    .scan-button.scanning {
       background: #6c757d;
       cursor: not-allowed;
    }
    .device-list {
      display: grid;
      gap: 16px;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    }
    .device-card {
      background: var(--card-background-color, #ffffff);
      border-radius: 16px;
      padding: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.05);
      border: 1px solid rgba(0,0,0,0.02);
    }
    .device-name {
      font-weight: 600;
      font-size: 1.1rem;
      margin-bottom: 4px;
    }
    .device-info {
        display: flex;
        flex-direction: column;
    }
    .device-address {
      font-size: 0.8rem;
      color: #666;
    }
    .connect-button {
      background: rgba(0,122,255, 0.1);
      color: #007aff;
      border: none;
      padding: 8px 16px;
      border-radius: 10px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
    }
    .connect-button:hover {
        background: rgba(0,122,255, 0.2);
    }
    .status-active {
        color: #34c759;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }
  `;

    render() {
        return html`
      <div class="header">
        <h1>EzBt Bluetooth</h1>
        <button 
            class="scan-button ${this.isScanning ? 'scanning' : ''}" 
            @click=${() => this.scanDevices()}
            ?disabled=${this.isScanning}
        >
          ${this.isScanning ? "Scanning..." : "Scan for Devices"}
        </button>
      </div>
      <div class="device-list">
        ${this.devices.map(
            (device) => html`
            <div class="device-card">
              <div class="device-info">
                <div class="device-name">${device.name}</div>
                <div class="device-address">${device.address}</div>
              </div>
              <div class="device-actions">
                  ${device.connected
                    ? html`<div class="status-active">
                        <span>●</span> Active
                        <button class="connect-button" @click=${() => this.disconnectDevice(device)}>Disconnect</button>
                      </div>`
                    : html`<button class="connect-button" @click=${() => this.pairDevice(device)}>Connect</button>`
                }
              </div>
            </div>
          `
        )}
      </div>
    `;
    }

    async scanDevices() {
        console.log("EzBt: Starting scan...");
        this.isScanning = true;
        try {
            const result = await this.hass.callWS({
                type: "call_service",
                domain: "ezbt",
                service: "scan",
                service_data: {},
                return_response: true,
            });
            
            console.log("EzBt: Scan result received:", result);
            
            // Handle variations in response structure
            if (result && result.response && result.response.devices) {
                this.devices = result.response.devices;
            } else if (result && result.devices) {
                this.devices = result.devices;
            } else if (result && typeof result === 'object' && !Array.isArray(result)) {
                // If the result is the response itself
                this.devices = result.devices || [];
            } else {
                this.devices = [];
            }
            console.log(`EzBt: Found ${this.devices.length} devices`);
        } catch (e) {
            console.error("EzBt: Scan failed", e);
        } finally {
            this.isScanning = false;
        }
    }

    async pairDevice(device) {
        try {
            await this.hass.callService("ezbt", "pair_device", { address: device.address });
            await this.scanDevices();
        } catch (e) {
            console.error("Pairing failed", e);
        }
    }

    async disconnectDevice(device) {
        try {
            await this.hass.callService("ezbt", "disconnect_device", { address: device.address });
            await this.scanDevices();
        } catch (e) {
            console.error("Disconnect failed", e);
        }
    }
}

customElements.define("ezbt-panel", EzBtPanel);
